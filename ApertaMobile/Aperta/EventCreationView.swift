import SwiftUI

struct EventCreationView: View {
    @State private var eventName = ""
    @State private var eventLocation = ""
    @State private var eventDate = Date()
    @State private var showRecordingView = false
    @State private var createdEvent: Event?
    @State private var eventCreated = false
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                // Header
                Text(eventCreated ? "Event Created" : "Create New Event")
                    .font(.largeTitle)
                    .bold()
                    .padding(.top, 40)
                
                Spacer()
                
                if !eventCreated {
                    // Form fields (before event creation)
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
                } else {
                    // Show created event details
                    VStack(spacing: 16) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Event Name")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text(eventName)
                                .font(.title3)
                                .bold()
                        }
                        
                        if !eventLocation.isEmpty {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Location")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                                HStack {
                                    Image(systemName: "location.fill")
                                    Text(eventLocation)
                                        .font(.body)
                                }
                            }
                        }
                        
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Date")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text(eventDate, style: .date)
                                .font(.body)
                        }
                    }
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(12)
                    .padding(.horizontal)
                }
                
                Spacer()
                
                // Action button
                if !eventCreated {
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
                    .padding(.bottom, 40)
                } else {
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
                ToolbarItem(placement: .navigationBarTrailing) {
                    NavigationLink(destination: PastEventsView()) {
                        Image(systemName: "clock.arrow.circlepath")
                            .font(.title2)
                    }
                }
            }
        }
    }
    
    private var canCreateEvent: Bool {
        !eventName.isEmpty
    }
    
    private func createEvent() {
        let event = Event(
            name: eventName,
            location: eventLocation.isEmpty ? "No location" : eventLocation,
            date: eventDate
        )
        createdEvent = event
        eventCreated = true
    }
    
    private func resetForm() {
        eventName = ""
        eventLocation = ""
        eventDate = Date()
        eventCreated = false
        createdEvent = nil
    }
}

#Preview {
    EventCreationView()
}
