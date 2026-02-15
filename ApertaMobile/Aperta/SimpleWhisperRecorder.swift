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
    @Published public private(set) var modelLoadingProgress: Double = 0
    @Published public private(set) var isModelLoaded = false
    @Published public private(set) var error: String?

    // MARK: - Private Properties
    private var audioEngine: AVAudioEngine?
    private var whisperKit: WhisperKit?
    private var recordingFile: AVAudioFile?
    private var currentRecordingURL: URL?
    private let audioProcessor = AudioProcessor()

    // Audio format - Whisper requires 16kHz mono
    private let sampleRate: Double = 16000

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

        guard let recordingURL = currentRecordingURL else {
            throw RecorderError.noRecordingFound
        }

        // Close the audio file to finalize it
        recordingFile = nil

        // Wait a moment for file to be fully written
        try await Task.sleep(nanoseconds: 100_000_000) // 0.1 second

        // Transcribe
        try await transcribe(audioFile: recordingURL)

        // Cleanup
        try? FileManager.default.removeItem(at: recordingURL)
        currentRecordingURL = nil
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

            // Extract text from segments
            transcriptionText = result.map { $0.text }.joined(separator: " ")
            isTranscribing = false

        } catch {
            isTranscribing = false
            self.error = "Transcription failed: \(error.localizedDescription)"
            throw error
        }
    }

    // MARK: - Cleanup

    public func cleanup() {
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

    public var errorDescription: String? {
        switch self {
        case .modelNotLoaded:
            return "Whisper model not loaded. Call loadModel() first."
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
