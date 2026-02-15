import Foundation
import Combine

/// Service for uploading audio files to the backend API
class AudioUploadService: NSObject, ObservableObject {
    static let shared = AudioUploadService()

    @Published var isUploading = false
    @Published var uploadProgress: Double = 0.0
    @Published var uploadError: String?
    @Published var uploadedConversationId: String?

    private let baseURL = "http://localhost:8000" // Change to your actual backend URL
    private var urlSession: URLSession

    private override init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 300 // 5 minute timeout
        config.timeoutIntervalForResource = 600 // 10 minute timeout
        config.waitsForConnectivity = true
        self.urlSession = URLSession(configuration: config)
        super.init()
    }

    // MARK: - Audio Upload

    /// Upload an audio file to the backend for processing
    /// - Parameters:
    ///   - audioFileURL: URL of the audio file to upload
    ///   - eventName: Name of the event (REQUIRED - determines transcript file)
    ///   - location: Location of the event (optional)
    ///   - conversationId: Optional existing conversation ID to update
    func uploadAudioFile(
        _ audioFileURL: URL,
        eventName: String,
        location: String? = nil,
        conversationId: String? = nil
    ) async -> Result<AudioUploadResponse, AudioUploadError> {
        do {
            // Validate file exists
            guard FileManager.default.fileExists(atPath: audioFileURL.path) else {
                return .failure(.fileNotFound)
            }

            // Read audio file
            let audioData = try Data(contentsOf: audioFileURL)
            let filename = audioFileURL.lastPathComponent

            // Build request
            var request = URLRequest(url: URL(string: "\(baseURL)/audio/process-event")!)
            request.httpMethod = "POST"

            // Create multipart form data
            let boundary = UUID().uuidString
            request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

            var body = Data()

            // Add file
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
            body.append("Content-Type: audio/\(filename.split(separator: ".").last ?? "mp4")\r\n\r\n".data(using: .utf8)!)
            body.append(audioData)
            body.append("\r\n".data(using: .utf8)!)

            // Add event_name (required)
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"event_name\"\r\n\r\n".data(using: .utf8)!)
            body.append("\(eventName)\r\n".data(using: .utf8)!)

            // Add optional parameters
            if let location = location {
                body.append("--\(boundary)\r\n".data(using: .utf8)!)
                body.append("Content-Disposition: form-data; name=\"location\"\r\n\r\n".data(using: .utf8)!)
                body.append("\(location)\r\n".data(using: .utf8)!)
            }

            if let conversationId = conversationId {
                body.append("--\(boundary)\r\n".data(using: .utf8)!)
                body.append("Content-Disposition: form-data; name=\"conversation_id\"\r\n\r\n".data(using: .utf8)!)
                body.append("\(conversationId)\r\n".data(using: .utf8)!)
            }

            body.append("--\(boundary)--\r\n".data(using: .utf8)!)
            request.httpBody = body

            // Update UI
            DispatchQueue.main.async {
                self.isUploading = true
                self.uploadError = nil
                self.uploadProgress = 0.0
            }

            // Perform request
            let (responseData, response) = try await urlSession.data(for: request)

            // Check response
            guard let httpResponse = response as? HTTPURLResponse else {
                return .failure(.invalidResponse)
            }

            if httpResponse.statusCode != 200 {
                let errorMessage = String(data: responseData, encoding: .utf8) ?? "Unknown error"
                return .failure(.serverError(errorMessage))
            }

            // Decode response
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            let uploadResponse = try decoder.decode(AudioUploadResponse.self, from: responseData)

            // Update UI
            DispatchQueue.main.async {
                self.uploadedConversationId = uploadResponse.conversation_id
                self.isUploading = false
                self.uploadProgress = 1.0
            }

            print("✅ Successfully uploaded audio: \(uploadResponse.message)")
            return .success(uploadResponse)

        } catch {
            DispatchQueue.main.async {
                self.isUploading = false
                self.uploadError = error.localizedDescription
            }
            return .failure(.processingError(error.localizedDescription))
        }
    }

    /// Get audio file from a conversation
    /// - Parameter conversationId: Conversation ID to fetch audio for
    func fetchAudioRecording(_ conversationId: String) async -> Result<AudioRecordingInfo, AudioUploadError> {
        do {
            let url = URL(string: "\(baseURL)/audio/recordings/\(conversationId)")!
            let (data, response) = try await urlSession.data(from: url)

            guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
                return .failure(.invalidResponse)
            }

            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            let recordingInfo = try decoder.decode(AudioRecordingInfo.self, from: data)
            return .success(recordingInfo)
        } catch {
            return .failure(.processingError(error.localizedDescription))
        }
    }
}

// MARK: - Data Models

struct AudioUploadResponse: Codable {
    let conversation_id: String
    let audio_recording: AudioRecordingData
    let transcription: TranscriptionData
    let ai_analysis: AIAnalysisData
    let message: String
}

struct AudioRecordingData: Codable {
    let id: String
    let conversation_id: String
    let file_path: String
    let file_size: Int
    let file_format: String
    let duration: Double
    let original_filename: String
    let processing_status: String
    let created_at: Date
}

struct TranscriptionData: Codable {
    let id: String
    let recording_id: String
    let conversation_id: String
    let raw_text: String?
    let formatted_text: String?
    let speaker_count: Int
    let speaker_names: [String: String]
    let segments: [[String: AnyCodable]]
    let confidence_score: Double?
    let sentiment: String?
    let summary: String?
    let entities: [AnyCodable]
    let action_items: [AnyCodable]
    let created_at: Date
}

struct AIAnalysisData: Codable {
    let summary: String?
    let sentiment: String?
    let entities: [AnyCodable]?
    let action_items: [AnyCodable]?
    let confidence_score: Double?
}

struct AudioRecordingInfo: Codable {
    let id: String
    let conversation_id: String
    let file_path: String
    let duration: Double
    let created_at: Date
}

// MARK: - Error Handling

enum AudioUploadError: LocalizedError {
    case fileNotFound
    case invalidResponse
    case serverError(String)
    case processingError(String)
    case networkError

    var errorDescription: String? {
        switch self {
        case .fileNotFound:
            return "Audio file not found"
        case .invalidResponse:
            return "Invalid response from server"
        case .serverError(let message):
            return "Server error: \(message)"
        case .processingError(let message):
            return "Processing error: \(message)"
        case .networkError:
            return "Network connection error"
        }
    }
}

// MARK: - AnyCodable Helper

enum AnyCodable: Codable {
    case null
    case bool(Bool)
    case int(Int)
    case double(Double)
    case string(String)
    case array([AnyCodable])
    case object([String: AnyCodable])

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if container.decodeNil() {
            self = .null
        } else if let value = try? container.decode(Bool.self) {
            self = .bool(value)
        } else if let value = try? container.decode(Int.self) {
            self = .int(value)
        } else if let value = try? container.decode(Double.self) {
            self = .double(value)
        } else if let value = try? container.decode(String.self) {
            self = .string(value)
        } else if let value = try? container.decode([AnyCodable].self) {
            self = .array(value)
        } else if let value = try? container.decode([String: AnyCodable].self) {
            self = .object(value)
        } else {
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Cannot decode AnyCodable")
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()

        switch self {
        case .null:
            try container.encodeNil()
        case .bool(let value):
            try container.encode(value)
        case .int(let value):
            try container.encode(value)
        case .double(let value):
            try container.encode(value)
        case .string(let value):
            try container.encode(value)
        case .array(let value):
            try container.encode(value)
        case .object(let value):
            try container.encode(value)
        }
    }
}
