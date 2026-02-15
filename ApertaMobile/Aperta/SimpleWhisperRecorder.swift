import Foundation
import AVFoundation
import WhisperKit
import Combine

/// Minimal Whisper transcription recorder for iOS
/// Handles microphone recording and transcription in one simple class
@MainActor
public class SimpleWhisperRecorder: ObservableObject {

    // MARK: - Published State
    @Published public private(set) var isRecording = false
    @Published public private(set) var isPaused = false
    @Published public private(set) var isTranscribing = false
    @Published public private(set) var transcriptionText = ""
    @Published public private(set) var originalTranscript = ""  // Unredacted
    @Published public private(set) var piiProtectionApplied = false
    @Published public private(set) var piiStats = ""
    @Published public private(set) var modelLoadingProgress: Double = 0
    @Published public private(set) var isModelLoaded = false
    @Published public private(set) var error: String?
    @Published public private(set) var audioLevel: Float = 0
    @Published public private(set) var recordingDuration: TimeInterval = 0

    // MARK: - Private Properties
    private var audioEngine: AVAudioEngine?
    private var whisperKit: WhisperKit?
    private var recordingFile: AVAudioFile?
    private var currentRecordingURL: URL?
    private let audioProcessor = AudioProcessor()
    private var recordingStartTime: Date?
    private var timerCancellable: AnyCancellable?
    private var transcriptSegments: [TranscriptSegment] = []

    // Audio format - Whisper requires 16kHz mono
    private let sampleRate: Double = 16000

    // MARK: - Recording Data
    public struct RecordingData {
        let audioFilePath: String
        let transcript: String
        let segments: [TranscriptSegment]
        let startTime: Date
        let endTime: Date
    }

    // MARK: - Initialization
    public init() {}

    // MARK: - Setup

    /// Load the Whisper model. Call this before recording.
    /// - Parameter modelName: Model variant (e.g., "tiny", "base", "small", "medium", "large")
    public func loadModel(variant: String = "base") async throws {
        do {
            error = nil
            modelLoadingProgress = 0

            // Initialize WhisperKit with automatic download and load
            whisperKit = try await WhisperKit(
                model: variant,
                verbose: true,
                logLevel: .debug,
                prewarm: true,
                load: true,
                download: true
            )

            modelLoadingProgress = 1.0
            isModelLoaded = true

        } catch {
            self.error = "Model loading failed: \(error.localizedDescription)"
            throw error
        }
    }

    // MARK: - Recording

    /// Start recording from the microphone
    public func startRecording() async throws {
        guard !isRecording else { return }
        guard isModelLoaded else {
            throw RecorderError.modelNotLoaded
        }

        do {
            error = nil

            // Request microphone permission
            let permission = await AVAudioApplication.requestRecordPermission()
            guard permission else {
                throw RecorderError.microphonePermissionDenied
            }

            // Configure audio session
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker, .allowBluetoothA2DP])
            try session.setActive(true)

            // Setup audio engine
            audioEngine = AVAudioEngine()
            guard let audioEngine else { return }

            let inputNode = audioEngine.inputNode
            let inputFormat = inputNode.outputFormat(forBus: 0)

            // Create output format (16kHz mono for Whisper)
            guard let outputFormat = AVAudioFormat(
                commonFormat: .pcmFormatFloat32,
                sampleRate: sampleRate,
                channels: 1,
                interleaved: false
            ) else {
                throw RecorderError.audioFormatError
            }

            // Create recording file
            currentRecordingURL = FileManager.default.temporaryDirectory
                .appendingPathComponent(UUID().uuidString)
                .appendingPathExtension("m4a")

            guard let recordingURL = currentRecordingURL else { return }

            recordingFile = try AVAudioFile(
                forWriting: recordingURL,
                settings: outputFormat.settings,
                commonFormat: outputFormat.commonFormat,
                interleaved: outputFormat.isInterleaved
            )

            // Create converter if needed
            let converter = AVAudioConverter(from: inputFormat, to: outputFormat)

            // Install tap to capture audio
            inputNode.installTap(onBus: 0, bufferSize: 4096, format: inputFormat) { [weak self] buffer, _ in
                guard let self, let recordingFile, let converter else { return }

                // Calculate audio level (RMS)
                Task { @MainActor in
                    self.audioLevel = self.calculateAudioLevel(buffer: buffer)
                }

                // Convert to target format
                let frameCapacity = AVAudioFrameCount(outputFormat.sampleRate) * buffer.frameLength / AVAudioFrameCount(inputFormat.sampleRate)
                guard let convertedBuffer = AVAudioPCMBuffer(pcmFormat: outputFormat, frameCapacity: frameCapacity) else { return }

                var error: NSError?
                converter.convert(to: convertedBuffer, error: &error) { _, outStatus in
                    outStatus.pointee = .haveData
                    return buffer
                }

                if error == nil {
                    try? recordingFile.write(from: convertedBuffer)
                }
            }

            // Start recording
            audioEngine.prepare()
            try audioEngine.start()
            isRecording = true

            // Start timer
            recordingStartTime = Date()
            startTimer()

        } catch {
            self.error = "Recording failed: \(error.localizedDescription)"
            throw error
        }
    }

    /// Pause recording
    public func pauseRecording() {
        guard isRecording && !isPaused else { return }
        audioEngine?.pause()
        isPaused = true
    }

    /// Resume recording
    public func resumeRecording() throws {
        guard isRecording && isPaused else { return }
        guard let audioEngine else { return }

        do {
            try audioEngine.start()
            isPaused = false
        } catch {
            self.error = "Failed to resume recording: \(error.localizedDescription)"
            throw error
        }
    }

    /// Stop recording and transcribe the audio
    public func stopRecordingAndTranscribe() async throws {
        guard isRecording else { return }

        // If paused, resume before stopping
        if isPaused {
            try? resumeRecording()
        }

        // Stop recording
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        isRecording = false
        isPaused = false

        // Stop timer
        stopTimer()
        audioLevel = 0

        guard let recordingURL = currentRecordingURL else {
            throw RecorderError.noRecordingFound
        }

        // Close the audio file to finalize it
        recordingFile = nil

        // Wait a moment for file to be fully written
        try await Task.sleep(nanoseconds: 100_000_000) // 0.1 second

        // Transcribe
        try await transcribe(audioFile: recordingURL)

        // Keep the audio file (don't delete it anymore)
        // It will be managed by EventStorageManager
        currentRecordingURL = nil
    }

    /// Stop recording, transcribe, and return recording data with saved audio file
    public func stopRecordingAndGetData() async throws -> RecordingData {
        guard let startTime = recordingStartTime else {
            throw RecorderError.notRecording
        }

        let endTime = Date()

        // Stop recording
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        isRecording = false
        isPaused = false

        // Stop timer
        stopTimer()
        audioLevel = 0

        guard let recordingURL = currentRecordingURL else {
            throw RecorderError.noRecordingFound
        }

        // Close the audio file to finalize it
        recordingFile = nil

        // Wait a moment for file to be fully written
        try await Task.sleep(nanoseconds: 100_000_000) // 0.1 second

        // Save audio file to persistent storage
        let savedAudioPath = try saveAudioFile(from: recordingURL)

        // Transcribe
        try await transcribe(audioFile: recordingURL)

        // Clean up temp file
        try? FileManager.default.removeItem(at: recordingURL)
        currentRecordingURL = nil

        // Return recording data
        return RecordingData(
            audioFilePath: savedAudioPath,
            transcript: transcriptionText,
            segments: transcriptSegments,
            startTime: startTime,
            endTime: endTime
        )
    }

    /// Save audio file to persistent documents directory
    private func saveAudioFile(from tempURL: URL) throws -> String {
        let fileManager = FileManager.default
        let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let recordingsDir = documentsURL.appendingPathComponent("recordings")

        // Create recordings directory if it doesn't exist
        if !fileManager.fileExists(atPath: recordingsDir.path) {
            try fileManager.createDirectory(at: recordingsDir, withIntermediateDirectories: true)
        }

        // Generate unique filename
        let filename = "\(UUID().uuidString).m4a"
        let destinationURL = recordingsDir.appendingPathComponent(filename)

        // Copy file
        try fileManager.copyItem(at: tempURL, to: destinationURL)

        // Return relative path
        return "recordings/\(filename)"
    }

    // MARK: - Transcription

    /// Transcribe an audio file
    public func transcribe(audioFile: URL) async throws {
        guard let whisperKit else {
            throw RecorderError.modelNotLoaded
        }

        do {
            error = nil
            isTranscribing = true
            transcriptionText = ""

            // Transcribe
            let result = try await whisperKit.transcribe(
                audioPath: audioFile.path(),
                decodeOptions: DecodingOptions(
                    task: .transcribe,
                    language: "en",
                    temperature: 0.0,
                    skipSpecialTokens: true,
                    withoutTimestamps: false
                )
            ) { progress in
                // Update progress if needed
                print("Transcription progress: \(progress)")
                return true  // Continue transcription
            }

            // Extract text from segments (result is an array of TranscriptionResult)
            let rawTranscript = result.map { $0.text }.joined(separator: " ")

            // Redact PII using PII Guardian
            print("🛡️ Running PII Guardian on transcript...")
            let redactedTranscript = try await LLMModelManager.shared.redactPII(from: rawTranscript)
            transcriptionText = redactedTranscript

            // Save segments for Recording model
            // Each TranscriptionResult has segments
            transcriptSegments = result.flatMap { $0.segments }.map { segment in
                TranscriptSegment(
                    text: segment.text,
                    startTime: Double(segment.start),
                    endTime: Double(segment.end)
                )
            }

            isTranscribing = false

        } catch {
            isTranscribing = false
            self.error = "Transcription failed: \(error.localizedDescription)"
            throw error
        }
    }

    // MARK: - PII Protection

    private func protectTranscript(_ transcript: String) async -> ProtectedTranscript {
        return await PIIProtectionManager.shared.protectTranscript(transcript)
    }

    // MARK: - Audio Level Monitoring

    private func calculateAudioLevel(buffer: AVAudioPCMBuffer) -> Float {
        guard let channelData = buffer.floatChannelData else { return 0 }
        let channelDataValue = channelData.pointee
        let frameLength = Int(buffer.frameLength)

        // Calculate RMS (Root Mean Square) for audio level
        var sum: Float = 0
        for i in 0..<frameLength {
            let sample = channelDataValue[i]
            sum += sample * sample
        }

        let rms = sqrt(sum / Float(frameLength))

        // Normalize to 0-1 range (typical speech is around 0.1-0.3)
        let normalized = min(rms * 10, 1.0)
        return normalized
    }

    private func startTimer() {
        timerCancellable = Timer.publish(every: 0.1, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                guard let self, let startTime = self.recordingStartTime else { return }
                if !self.isPaused {
                    self.recordingDuration = Date().timeIntervalSince(startTime)
                }
            }
    }

    private func stopTimer() {
        timerCancellable?.cancel()
        timerCancellable = nil
        recordingDuration = 0
        recordingStartTime = nil
    }

    // MARK: - Cleanup

    public func cleanup() {
        stopTimer()
        audioEngine?.stop()
        audioEngine = nil

        if let recordingURL = currentRecordingURL {
            try? FileManager.default.removeItem(at: recordingURL)
        }
    }
}

// MARK: - Errors

public enum RecorderError: LocalizedError {
    case modelNotLoaded
    case modelInitFailed
    case microphonePermissionDenied
    case audioFormatError
    case noRecordingFound
    case notRecording

    public var errorDescription: String? {
        switch self {
        case .modelNotLoaded:
            return "Whisper model not loaded. Call loadModel() first."
        case .notRecording:
            return "Not currently recording."
        case .modelInitFailed:
            return "Failed to initialize WhisperKit."
        case .microphonePermissionDenied:
            return "Microphone permission denied."
        case .audioFormatError:
            return "Failed to create audio format."
        case .noRecordingFound:
            return "No recording found to transcribe."
        }
    }
}
