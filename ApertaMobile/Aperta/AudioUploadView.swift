import SwiftUI

/// View for uploading audio files to the backend
struct AudioUploadView: View {
    @StateObject private var uploadService = AudioUploadService.shared
    @State private var showingFilePicker = false
    @State private var selectedAudioURL: URL?
    @State private var eventName: String = ""
    @State private var location: String = ""
    @State private var showSuccess = false
    @State private var showError = false

    var event: Event

    var body: some View {
        VStack(spacing: 20) {
            // Header
            VStack(alignment: .leading, spacing: 8) {
                Text("Upload Event Audio")
                    .font(.title2)
                    .fontWeight(.bold)
                Text("Recording from \(event.name)")
                    .font(.caption)
                    .foregroundColor(.gray)
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            // Event Info
            VStack(spacing: 12) {
                InfoRow(label: "Event", value: event.name)
                InfoRow(label: "Location", value: event.location)
                InfoRow(label: "Date", value: dateFormatter.string(from: event.date))
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(8)

            // File Selection
            VStack(spacing: 12) {
                if let audioURL = selectedAudioURL {
                    HStack {
                        Image(systemName: "waveform")
                            .foregroundColor(.blue)
                        VStack(alignment: .leading, spacing: 4) {
                            Text(audioURL.lastPathComponent)
                                .font(.caption)
                                .fontWeight(.semibold)
                            Text(fileSize(audioURL))
                                .font(.caption2)
                                .foregroundColor(.gray)
                        }
                        Spacer()
                        Button(action: { selectedAudioURL = nil }) {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.gray)
                        }
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
                } else {
                    Button(action: { showingFilePicker = true }) {
                        HStack {
                            Image(systemName: "doc.badge.plus")
                            Text("Select Audio File")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                    }
                }
            }

            // Optional Fields
            VStack(spacing: 12) {
                Text("Additional Info (Optional)")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .frame(maxWidth: .infinity, alignment: .leading)

                TextField("Event Name (optional)", text: $eventName)
                    .textFieldStyle(.roundedBorder)
                    .placeholder(when: eventName.isEmpty) {
                        Text(event.name).foregroundColor(.gray)
                    }

                TextField("Location (optional)", text: $location)
                    .textFieldStyle(.roundedBorder)
                    .placeholder(when: location.isEmpty) {
                        Text(event.location).foregroundColor(.gray)
                    }
            }

            // Status
            if uploadService.isUploading {
                VStack(spacing: 12) {
                    ProgressView(value: uploadService.uploadProgress)
                        .tint(.blue)
                    Text("Uploading and processing... \(Int(uploadService.uploadProgress * 100))%")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
            } else if let error = uploadService.uploadError {
                HStack {
                    Image(systemName: "exclamationmark.circle.fill")
                        .foregroundColor(.red)
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                }
                .padding()
                .background(Color(.systemRed).opacity(0.1))
                .cornerRadius(8)
            }

            Spacer()

            // Upload Button
            Button(action: uploadAudio) {
                HStack {
                    if uploadService.isUploading {
                        ProgressView()
                            .progressViewStyle(.circular)
                            .tint(.white)
                    } else {
                        Image(systemName: "arrow.up.circle.fill")
                    }
                    Text(uploadService.isUploading ? "Uploading..." : "Upload Audio")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(selectedAudioURL != nil && !uploadService.isUploading ? Color.blue : Color.gray)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
            .disabled(selectedAudioURL == nil || uploadService.isUploading)

            if let conversationId = uploadService.uploadedConversationId {
                VStack(spacing: 8) {
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                        Text("Successfully uploaded!")
                            .font(.caption)
                            .fontWeight(.semibold)
                    }
                    Text("Conversation ID: \(conversationId)")
                        .font(.caption2)
                        .foregroundColor(.gray)
                        .textSelection(.enabled)
                }
                .padding()
                .background(Color(.systemGreen).opacity(0.1))
                .cornerRadius(8)
            }
        }
        .padding()
        .fileImporter(
            isPresented: $showingFilePicker,
            allowedContentTypes: [.audio, .mp3, .wav, .m4a],
            onCompletion: { result in
                switch result {
                case .success(let url):
                    selectedAudioURL = url
                case .failure(let error):
                    uploadService.uploadError = error.localizedDescription
                }
            }
        )
    }

    // MARK: - Helper Methods

    private func uploadAudio() {
        guard let audioURL = selectedAudioURL else { return }

        Task {
            let result = await uploadService.uploadAudioFile(
                audioURL,
                eventName: eventName.isEmpty ? event.name : eventName,
                location: location.isEmpty ? event.location : location,
                conversationId: nil
            )

            switch result {
            case .success(let response):
                print("✅ Upload successful: \(response.conversation_id)")
            case .failure(let error):
                print("❌ Upload failed: \(error.localizedDescription)")
            }
        }
    }

    private func fileSize(_ url: URL) -> String {
        let attributes = try? FileManager.default.attributesOfItem(atPath: url.path)
        guard let fileSize = attributes?[.size] as? Int else { return "Unknown size" }

        let formatter = ByteCountFormatter()
        formatter.allowedUnits = [.useMB, .useKB]
        formatter.countStyle = .file
        return formatter.string(fromByteCount: Int64(fileSize))
    }

    private var dateFormatter: DateFormatter {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        return formatter
    }
}

// MARK: - Helper Views

struct InfoRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .font(.caption)
                .foregroundColor(.gray)
            Spacer()
            Text(value)
                .font(.caption)
                .fontWeight(.semibold)
        }
    }
}

// MARK: - Preview

#Preview {
    AudioUploadView(event: Event(
        id: UUID(),
        name: "TechConf 2024",
        location: "San Francisco, CA",
        date: Date()
    ))
}
