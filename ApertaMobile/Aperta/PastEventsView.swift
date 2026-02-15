import SwiftUI
import UniformTypeIdentifiers

struct PastEventsView: View {
    @State private var events: [Event] = []
    @State private var eventToDelete: Event?
    @State private var showDeleteConfirmation = false
    @State private var searchText = ""

    private var filteredEvents: [Event] {
        if searchText.isEmpty {
            return events
        } else {
            return events.filter { event in
                event.name.localizedCaseInsensitiveContains(searchText) ||
                event.location.localizedCaseInsensitiveContains(searchText)
            }
        }
    }

    var body: some View {
        List {
            if filteredEvents.isEmpty && !searchText.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 60))
                        .foregroundColor(.gray)
                    Text("No events found")
                        .font(.headline)
                        .foregroundColor(.gray)
                    Text("Try a different search term")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
                .frame(maxWidth: .infinity)
                .padding(.top, 100)
                .listRowBackground(Color.clear)
            } else if events.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "calendar.badge.clock")
                        .font(.system(size: 60))
                        .foregroundColor(.gray)
                    Text("No past events yet")
                        .font(.headline)
                        .foregroundColor(.gray)
                    Text("Your recorded events will appear here")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
                .frame(maxWidth: .infinity)
                .padding(.top, 100)
                .listRowBackground(Color.clear)
            } else {
                ForEach(filteredEvents) { event in
                    NavigationLink(destination: EventDetailView(event: event)) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text(event.name)
                                .font(.headline)
                            HStack {
                                Image(systemName: "location.fill")
                                    .font(.caption)
                                Text(event.location)
                                    .font(.subheadline)
                                    .foregroundColor(.gray)
                            }
                            Text(event.date, style: .date)
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        .padding(.vertical, 4)
                    }
                    .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                        Button(role: .destructive) {
                            eventToDelete = event
                            showDeleteConfirmation = true
                        } label: {
                            Label("Delete", systemImage: "trash")
                        }
                    }
                }
            }
        }
        .navigationTitle("Past Events")
        .searchable(text: $searchText, prompt: "Search events by name or location")
        .onAppear {
            loadEvents()
        }
        .confirmationDialog(
            "Delete Event",
            isPresented: $showDeleteConfirmation,
            presenting: eventToDelete
        ) { event in
            Button("Delete", role: .destructive) {
                deleteEvent(event)
            }
            Button("Cancel", role: .cancel) {}
        } message: { event in
            Text("Are you sure you want to delete '\(event.name)'? This action cannot be undone.")
        }
    }

    private func deleteEvent(_ event: Event) {
        do {
            try EventStorageManager.shared.deleteEvent(event)
            events.removeAll { $0.id == event.id }
            print("✅ Deleted event: \(event.name)")
        } catch {
            print("❌ Failed to delete event: \(error)")
        }
    }

    private func loadEvents() {
        do {
            events = try EventStorageManager.shared.loadAllEvents()
            print("✅ Loaded \(events.count) events")
        } catch {
            print("❌ Failed to load events: \(error)")
        }
    }
}

struct EventDetailView: View {
    let event: Event
    @State private var showRecordingView = false
    @State private var refreshedEvent: Event?
    @State private var recordingToDelete: Recording?
    @State private var recordingToRename: Recording?
    @State private var newRecordingName = ""
    @State private var showDeleteConfirmation = false
    @State private var showRenameDialog = false
    @State private var showFileImporter = false
    @State private var isTranscribing = false
    @State private var transcriptionProgress: Double = 0
    @State private var transcriptionError: String?
    @State private var showTranscriptionError = false
    @StateObject private var fileTranscriber = FileTranscriber()

    private var displayEvent: Event {
        refreshedEvent ?? event
    }

    var body: some View {
        List {
            Section("Event Details") {
                LabeledContent("Name", value: displayEvent.name)
                LabeledContent("Location", value: displayEvent.location)
                LabeledContent("Date", value: displayEvent.date, format: .dateTime)
            }

            Section {
                Button(action: {
                    showRecordingView = true
                }) {
                    HStack {
                        Image(systemName: "mic.circle.fill")
                            .foregroundColor(.blue)
                        Text("Record New Audio")
                            .foregroundColor(.primary)
                        Spacer()
                        Image(systemName: "chevron.right")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                }

                Button(action: {
                    showFileImporter = true
                }) {
                    HStack {
                        Image(systemName: "doc.badge.plus")
                            .foregroundColor(.green)
                        Text("Add Recording from File")
                            .foregroundColor(.primary)
                        Spacer()
                        Image(systemName: "chevron.right")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                }
            }

            Section("Recordings (\(displayEvent.recordings.count))") {
                if displayEvent.recordings.isEmpty {
                    Text("No recordings yet")
                        .foregroundColor(.gray)
                        .italic()
                } else {
                    ForEach(Array(displayEvent.recordings.enumerated()), id: \.element.id) { index, recording in
                        NavigationLink(destination: TranscriptDetailView(recording: recording)) {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(recording.name.isEmpty ? "Recording \(index + 1)" : recording.name)
                                    .font(.headline)
                                HStack(spacing: 12) {
                                    if let duration = recording.duration {
                                        HStack(spacing: 4) {
                                            Image(systemName: "clock")
                                                .font(.caption2)
                                            Text(formatDuration(duration))
                                        }
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                    }
                                    HStack(spacing: 4) {
                                        Image(systemName: "text.quote")
                                            .font(.caption2)
                                        Text("\(recording.transcript.count) chars")
                                    }
                                    .font(.caption)
                                    .foregroundColor(.gray)
                                }
                            }
                        }
                        .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                            Button(role: .destructive) {
                                recordingToDelete = recording
                                showDeleteConfirmation = true
                            } label: {
                                Label("Delete", systemImage: "trash")
                            }
                        }
                        .swipeActions(edge: .leading, allowsFullSwipe: false) {
                            Button {
                                recordingToRename = recording
                                newRecordingName = recording.name.isEmpty ? "Recording \(index + 1)" : recording.name
                                showRenameDialog = true
                            } label: {
                                Label("Rename", systemImage: "pencil")
                            }
                            .tint(.blue)
                        }
                    }
                }
            }
        }
        .navigationTitle(displayEvent.name)
        .navigationBarTitleDisplayMode(.large)
        .navigationDestination(isPresented: $showRecordingView) {
            RecordingView(event: displayEvent, onEndEvent: {
                showRecordingView = false
                refreshEvent()
            })
        }
        .onAppear {
            refreshEvent()
        }
        .alert("Delete Recording", isPresented: $showDeleteConfirmation) {
            Button("Cancel", role: .cancel) {
                recordingToDelete = nil
            }
            Button("Delete", role: .destructive) {
                if let recording = recordingToDelete {
                    deleteRecording(recording)
                }
            }
        } message: {
            Text("Are you sure you want to delete this recording? This action cannot be undone.")
        }
        .sheet(isPresented: $showRenameDialog) {
            NavigationStack {
                VStack(spacing: 20) {
                    Text("Rename Recording")
                        .font(.headline)
                        .padding(.top)

                    TextField("Recording name", text: $newRecordingName)
                        .textFieldStyle(.roundedBorder)
                        .padding(.horizontal)

                    Spacer()
                }
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button("Cancel") {
                            showRenameDialog = false
                            recordingToRename = nil
                        }
                    }
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Save") {
                            if let recording = recordingToRename {
                                renameRecording(recording, newName: newRecordingName)
                            }
                            showRenameDialog = false
                        }
                        .disabled(newRecordingName.isEmpty)
                    }
                }
            }
            .presentationDetents([.height(200)])
        }
        .fileImporter(
            isPresented: $showFileImporter,
            allowedContentTypes: [.audio, .mp3, .wav, .mpeg4Audio],
            allowsMultipleSelection: false
        ) { result in
            handleFileSelection(result)
        }
        .overlay {
            if isTranscribing {
                ZStack {
                    Color.black.opacity(0.4)
                        .ignoresSafeArea()

                    VStack(spacing: 20) {
                        ProgressView(value: transcriptionProgress)
                            .progressViewStyle(.linear)
                            .frame(width: 200)

                        VStack(spacing: 8) {
                            Text("Transcribing Audio")
                                .font(.headline)
                            Text(progressMessage)
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                    }
                    .padding(30)
                    .background(Color(.systemBackground))
                    .cornerRadius(16)
                    .shadow(radius: 20)
                }
            }
        }
        .alert("Transcription Error", isPresented: $showTranscriptionError) {
            Button("OK") { transcriptionError = nil }
        } message: {
            Text(transcriptionError ?? "Unknown error occurred")
        }
    }

    private var progressMessage: String {
        if transcriptionProgress < 0.3 {
            return "Loading Whisper model..."
        } else if transcriptionProgress < 0.6 {
            return "Processing audio..."
        } else if transcriptionProgress < 0.9 {
            return "Running PII protection..."
        } else {
            return "Saving recording..."
        }
    }

    private func handleFileSelection(_ result: Result<[URL], Error>) {
        switch result {
        case .success(let urls):
            guard let fileURL = urls.first else { return }

            Task {
                await transcribeFile(fileURL)
            }

        case .failure(let error):
            transcriptionError = "Failed to select file: \(error.localizedDescription)"
            showTranscriptionError = true
        }
    }

    private func transcribeFile(_ fileURL: URL) async {
        isTranscribing = true
        transcriptionProgress = 0.1

        do {
            // Load Whisper model
            transcriptionProgress = 0.2
            try await fileTranscriber.loadModel(variant: "small")

            // Load PII Guardian
            transcriptionProgress = 0.3
            try await LLMModelManager.shared.loadModel()

            // Transcribe the file
            transcriptionProgress = 0.4
            let recordingData = try await fileTranscriber.transcribeFile(
                fileURL: fileURL,
                progressCallback: { progress in
                    Task { @MainActor in
                        transcriptionProgress = 0.4 + (progress * 0.4) // 0.4 to 0.8
                    }
                }
            )

            // Run PII protection
            transcriptionProgress = 0.8
            let protectedTranscript = try await LLMModelManager.shared.redactPII(from: recordingData.transcript)

            // Create recording with proper duration
            transcriptionProgress = 0.9
            let startTime = Date()
            var newRecording = Recording(
                name: fileURL.deletingPathExtension().lastPathComponent,
                transcript: protectedTranscript,
                segments: recordingData.segments,
                audioFilePath: recordingData.audioFilePath,
                startTime: startTime
            )
            newRecording.endTime = startTime.addingTimeInterval(recordingData.duration)

            // Save to event
            var updatedEvent = displayEvent
            updatedEvent.recordings.append(newRecording)
            try EventStorageManager.shared.saveEvent(updatedEvent)

            transcriptionProgress = 1.0
            refreshedEvent = updatedEvent

            print("✅ File transcribed and saved: \(newRecording.name)")

            // Upload transcript to GCS
            print("📤 Uploading transcript to cloud...")
            let uploadResult = await AudioUploadService.shared.uploadTranscriptOnly(
                transcriptText: protectedTranscript,
                eventName: displayEvent.name,
                location: displayEvent.location
            )

            switch uploadResult {
            case .success(let response):
                print("✅ Transcript uploaded to GCS: \(response.transcript_file_path)")
            case .failure(let error):
                print("⚠️ Transcript upload failed (file still saved locally): \(error.localizedDescription)")
            }

            // Wait a moment to show completion
            try await Task.sleep(nanoseconds: 500_000_000)
            isTranscribing = false

        } catch {
            isTranscribing = false
            transcriptionError = error.localizedDescription
            showTranscriptionError = true
            print("❌ Transcription error: \(error)")
        }
    }

    private func refreshEvent() {
        // Reload the event from storage to get updated recordings
        do {
            let allEvents = try EventStorageManager.shared.loadAllEvents()
            refreshedEvent = allEvents.first { $0.id == event.id }
        } catch {
            print("❌ Failed to refresh event: \(error)")
        }
    }

    private func deleteRecording(_ recording: Recording) {
        guard var updatedEvent = refreshedEvent ?? allEvents.first(where: { $0.id == event.id }) else { return }

        updatedEvent.recordings.removeAll { $0.id == recording.id }

        do {
            try EventStorageManager.shared.saveEvent(updatedEvent)
            refreshedEvent = updatedEvent
            print("✅ Recording deleted: \(recording.id)")

            // Delete audio file if it exists
            if let audioPath = recording.audioFilePath {
                let fileManager = FileManager.default
                let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
                let audioURL = documentsURL.appendingPathComponent(audioPath)
                try? fileManager.removeItem(at: audioURL)
                print("🗑️ Audio file deleted: \(audioPath)")
            }
        } catch {
            print("❌ Error deleting recording: \(error)")
        }

        recordingToDelete = nil
    }

    private func renameRecording(_ recording: Recording, newName: String) {
        guard var updatedEvent = refreshedEvent ?? allEvents.first(where: { $0.id == event.id }) else { return }

        if let index = updatedEvent.recordings.firstIndex(where: { $0.id == recording.id }) {
            updatedEvent.recordings[index].name = newName

            do {
                try EventStorageManager.shared.saveEvent(updatedEvent)
                refreshedEvent = updatedEvent
                print("✅ Recording renamed: \(recording.id) -> \(newName)")
            } catch {
                print("❌ Error renaming recording: \(error)")
            }
        }

        recordingToRename = nil
    }

    private var allEvents: [Event] {
        (try? EventStorageManager.shared.loadAllEvents()) ?? []
    }

    private func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        let seconds = Int(duration) % 60
        return "\(minutes)m \(seconds)s"
    }
}

struct TranscriptDetailView: View {
    let recording: Recording
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Recording info
                VStack(alignment: .leading, spacing: 8) {
                    Text("Started: \(recording.startTime, style: .time)")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                    if let endTime = recording.endTime {
                        Text("Ended: \(endTime, style: .time)")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    if let duration = recording.duration {
                        Text("Duration: \(formatDuration(duration))")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                }
                .padding()
                
                Divider()
                
                // Transcript with timestamps
                VStack(alignment: .leading, spacing: 12) {
                    Text("Transcript")
                        .font(.headline)
                        .padding(.horizontal)
                    
                    if recording.segments.isEmpty {
                        Text(recording.transcript)
                            .padding()
                    } else {
                        ForEach(recording.segments) { segment in
                            HStack(alignment: .top, spacing: 12) {
                                Text(formatTimestamp(segment.startTime))
                                    .font(.caption)
                                    .foregroundColor(.blue)
                                    .frame(width: 60, alignment: .leading)
                                
                                Text(segment.text)
                                    .font(.body)
                                
                                Spacer()
                            }
                            .padding(.horizontal)
                        }
                    }
                }
            }
        }
        .navigationTitle("Transcript")
    }
    
    private func formatTimestamp(_ seconds: Double) -> String {
        let minutes = Int(seconds) / 60
        let secs = Int(seconds) % 60
        return String(format: "%d:%02d", minutes, secs)
    }
    
    private func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        let seconds = Int(duration) % 60
        return "\(minutes)m \(seconds)s"
    }
}

#Preview {
    NavigationStack {
        PastEventsView()
    }
}
