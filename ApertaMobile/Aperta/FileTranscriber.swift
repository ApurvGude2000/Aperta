// ABOUTME: Transcribes audio files using WhisperKit (no recording, just file processing)
// ABOUTME: Used for importing existing audio files into events

import Foundation
import AVFoundation
import WhisperKit
import Combine

/// Transcribes audio files using WhisperKit without live recording
@MainActor
public class FileTranscriber: ObservableObject {
    @Published public private(set) var isModelLoaded = false
    @Published public private(set) var isTranscribing = false
    @Published public private(set) var error: String?

    private var whisperKit: WhisperKit?

    public init() {}

    // MARK: - Setup

    /// Load the Whisper model
    public func loadModel(variant: String = "base") async throws {
        guard !isModelLoaded else { return }

        do {
            error = nil

            whisperKit = try await WhisperKit(
                model: variant,
                verbose: true,
                logLevel: .debug,
                prewarm: true,
                load: true,
                download: true
            )

            isModelLoaded = true
            print("✅ FileTranscriber: Whisper model loaded")

        } catch {
            self.error = "Model loading failed: \(error.localizedDescription)"
            throw error
        }
    }

    // MARK: - Transcription

    public struct TranscriptionData {
        let transcript: String
        let segments: [TranscriptSegment]
        let audioFilePath: String
        let duration: TimeInterval
    }

    /// Transcribe an audio file
    public func transcribeFile(
        fileURL: URL,
        progressCallback: ((Double) -> Void)? = nil
    ) async throws -> TranscriptionData {
        guard isModelLoaded, let whisperKit else {
            throw TranscriberError.modelNotLoaded
        }

        do {
            error = nil
            isTranscribing = true

            // Copy file to app's documents directory
            let savedPath = try saveAudioFile(from: fileURL)

            // Get the full URL for the saved file
            let fileManager = FileManager.default
            let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
            let savedURL = documentsURL.appendingPathComponent(savedPath)

            // Get audio duration
            let audioDuration = try getAudioDuration(from: savedURL)

            // Transcribe
            let result = try await whisperKit.transcribe(
                audioPath: savedURL.path(),
                decodeOptions: DecodingOptions(
                    task: .transcribe,
                    language: "en",
                    temperature: 0.0,
                    skipSpecialTokens: true,
                    withoutTimestamps: false
                )
            ) { progress in
                // Simple progress reporting (WhisperKit provides detailed progress internally)
                print("Transcription progress: \(progress)")
                // Just report incremental progress
                progressCallback?(0.5) // Midpoint of transcription phase
                return true
            }

            // Extract text
            let transcript = result.map { $0.text }.joined(separator: " ")

            // Extract segments
            let segments = result.flatMap { $0.segments }.map { segment in
                TranscriptSegment(
                    text: segment.text,
                    startTime: Double(segment.start),
                    endTime: Double(segment.end)
                )
            }

            isTranscribing = false

            return TranscriptionData(
                transcript: transcript,
                segments: segments,
                audioFilePath: savedPath,
                duration: audioDuration
            )

        } catch {
            isTranscribing = false
            self.error = "Transcription failed: \(error.localizedDescription)"
            throw error
        }
    }

    // MARK: - File Management

    /// Get the duration of an audio file
    private func getAudioDuration(from url: URL) throws -> TimeInterval {
        let audioFile = try AVAudioFile(forReading: url)
        let sampleRate = audioFile.fileFormat.sampleRate
        let frameCount = audioFile.length
        let duration = Double(frameCount) / sampleRate
        return duration
    }

    /// Save audio file to persistent documents directory
    private func saveAudioFile(from sourceURL: URL) throws -> String {
        let fileManager = FileManager.default
        let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let recordingsDir = documentsURL.appendingPathComponent("recordings")

        // Create recordings directory if it doesn't exist
        if !fileManager.fileExists(atPath: recordingsDir.path) {
            try fileManager.createDirectory(at: recordingsDir, withIntermediateDirectories: true)
        }

        // Access security-scoped resource
        let accessGranted = sourceURL.startAccessingSecurityScopedResource()
        defer {
            if accessGranted {
                sourceURL.stopAccessingSecurityScopedResource()
            }
        }

        // Get file extension
        let fileExtension = sourceURL.pathExtension.isEmpty ? "m4a" : sourceURL.pathExtension

        // Generate unique filename
        let filename = "\(UUID().uuidString).\(fileExtension)"
        let destinationURL = recordingsDir.appendingPathComponent(filename)

        // Copy file
        try fileManager.copyItem(at: sourceURL, to: destinationURL)

        print("✅ Audio file saved: \(filename)")

        // Return relative path
        return "recordings/\(filename)"
    }
}

// MARK: - Errors

public enum TranscriberError: LocalizedError {
    case modelNotLoaded
    case transcriptionFailed
    case fileNotFound

    public var errorDescription: String? {
        switch self {
        case .modelNotLoaded:
            return "Whisper model not loaded."
        case .transcriptionFailed:
            return "Failed to transcribe audio file."
        case .fileNotFound:
            return "Audio file not found."
        }
    }
}
