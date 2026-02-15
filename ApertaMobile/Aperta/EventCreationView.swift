import SwiftUI

struct EventCreationView: View {
    @State private var eventName = ""
    @State private var eventLocation = ""
    @State private var eventDate = Date()
    @State private var showRecordingView = false
    @State private var createdEvent: Event?
    @State private var eventCreated = false
    @State private var showCreateForm = false
    @State private var recentEvents: [Event] = []
    @State private var showSettings = false
    @AppStorage("appearanceMode") private var appearanceMode: AppearanceMode = .system

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                // Header
                if !showCreateForm && !eventCreated {
                    // Welcome screen
                    welcomeView
                } else {
                    Text(eventCreated ? "Event Created" : "Create New Event")
                        .font(.largeTitle)
                        .bold()
                        .padding(.top, 40)
                }
                
                Spacer()

                if !eventCreated && showCreateForm {
                    // Form fields (when creating event)
                    VStack(spacing: 20) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Event Name *")
                                .font(.headline)
                            TextField("Conference name", text: $eventName)
                                .textFieldStyle(.roundedBorder)
                                .padding(.horizontal)
                        }
                        
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Location (Optional)")
                                .font(.headline)
                            TextField("Venue or city", text: $eventLocation)
                                .textFieldStyle(.roundedBorder)
                                .padding(.horizontal)
                        }
                        
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Date")
                                .font(.headline)
                            DatePicker("", selection: $eventDate, displayedComponents: [.date])
                                .datePickerStyle(.compact)
                                .padding(.horizontal)
                        }
                    }
                    .padding()
                }
                
                Spacer()

                // Action buttons
                if !eventCreated && showCreateForm {
                    // Create Event button
                    Button(action: {
                        createEvent()
                    }) {
                        Text("Create Event")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(canCreateEvent ? Color.green : Color.gray)
                            .cornerRadius(12)
                    }
                    .disabled(!canCreateEvent)
                    .padding(.horizontal)

                    Button(action: {
                        showCreateForm = false
                    }) {
                        Text("Cancel")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.gray.opacity(0.2))
                            .foregroundColor(.primary)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal)
                    .padding(.bottom, 40)
                } else if eventCreated {
                    // Start Recording button (only after event created)
                    Button(action: {
                        showRecordingView = true
                    }) {
                        HStack {
                            Image(systemName: "play.circle.fill")
                            Text("Start Event")
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(12)
                    }
                    .padding(.horizontal)
                    
                    Button(action: {
                        resetForm()
                    }) {
                        Text("Cancel")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.gray.opacity(0.2))
                            .foregroundColor(.primary)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal)
                    .padding(.bottom, 40)
                }
            }
            .navigationDestination(isPresented: $showRecordingView) {
                if let event = createdEvent {
                    RecordingView(event: event, onEndEvent: resetForm)
                }
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: {
                        showSettings = true
                    }) {
                        Image(systemName: "gearshape")
                            .font(.title3)
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    NavigationLink(destination: PastEventsView()) {
                        HStack(spacing: 6) {
                            Image(systemName: "clock.arrow.circlepath")
                            Text("Past Events")
                                .font(.subheadline)
                        }
                    }
                }
            }
            .sheet(isPresented: $showSettings) {
                SettingsView()
            }
            .preferredColorScheme(appearanceMode.colorScheme)
            .onAppear {
                loadRecentEvents()
            }
        }
    }

    // MARK: - Welcome View

    private var welcomeView: some View {
        VStack(spacing: 32) {
            // App branding
            VStack(spacing: 16) {
                Image("aperta-logo")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 100, height: 100)

                VStack(spacing: 4) {
                    Text("Agent Echo")
                        .font(.system(size: 36, weight: .bold))
                    Text("by Aperta")
                        .font(.title3)
                        .foregroundColor(.gray)
                }

                Text("Record, transcribe, and master\nyour networking conversations")
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
                    .padding(.top, 4)
            }
            .padding(.top, 60)

            // Quick stats
            if !recentEvents.isEmpty {
                HStack(spacing: 40) {
                    VStack {
                        Text("\(recentEvents.count)")
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(.blue)
                        Text("Events")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }

                    VStack {
                        Text("\(totalRecordings)")
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(.green)
                        Text("Recordings")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.05))
                .cornerRadius(16)
            }

            Spacer()

            // Action buttons
            VStack(spacing: 16) {
                Button(action: {
                    showCreateForm = true
                }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text("Create New Event")
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(12)
                }

                // Continue Last Event button (if available)
                if let lastEvent = recentEvents.first {
                    NavigationLink(destination: EventDetailView(event: lastEvent)) {
                        HStack(spacing: 12) {
                            Image(systemName: "arrow.clockwise.circle.fill")
                                .font(.title2)
                                .foregroundColor(.blue)
                            VStack(alignment: .leading, spacing: 2) {
                                Text("Continue Last Event")
                                    .font(.subheadline)
                                    .fontWeight(.medium)
                                    .foregroundColor(.primary)
                                Text(lastEvent.name)
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(12)
                    }
                }
            }
            .padding(.horizontal)

            // Copyright footer
            Text("Aperta 2026 All rights reserved")
                .font(.caption2)
                .foregroundColor(.gray.opacity(0.6))
                .padding(.bottom, 20)
        }
    }

    private var totalRecordings: Int {
        recentEvents.reduce(0) { $0 + $1.recordings.count }
    }

    // MARK: - Computed Properties

    private var canCreateEvent: Bool {
        !eventName.isEmpty
    }
    
    private func createEvent() {
        let event = Event(
            name: eventName,
            location: eventLocation.isEmpty ? "No location" : eventLocation,
            date: eventDate
        )

        // Save event to local storage
        do {
            try EventStorageManager.shared.saveEvent(event)
            print("✅ Event saved successfully!")
        } catch {
            print("❌ Failed to save event: \(error)")
        }

        createdEvent = event
        eventCreated = true
    }
    
    private func loadRecentEvents() {
        do {
            recentEvents = try EventStorageManager.shared.loadAllEvents()
        } catch {
            print("❌ Failed to load recent events: \(error)")
        }
    }

    private func resetForm() {
        eventName = ""
        eventLocation = ""
        eventDate = Date()
        eventCreated = false
        createdEvent = nil
        showCreateForm = false
        loadRecentEvents()
    }
}

#Preview {
    EventCreationView()
}
