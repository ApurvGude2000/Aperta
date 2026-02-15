// ABOUTME: Settings screen for app configuration and preferences
// ABOUTME: Includes appearance settings, audio settings, and other app preferences

import SwiftUI

struct SettingsView: View {
    @AppStorage("appearanceMode") private var appearanceMode: AppearanceMode = .system
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            List {
                Section {
                    Picker("Appearance", selection: $appearanceMode) {
                        ForEach(AppearanceMode.allCases, id: \.self) { mode in
                            Text(mode.displayName).tag(mode)
                        }
                    }
                    .pickerStyle(.segmented)
                } header: {
                    Text("Display")
                } footer: {
                    Text("Choose how the app appears on your device")
                }

                Section {
                    NavigationLink {
                        PlaceholderSettingView(title: "Audio Quality")
                    } label: {
                        HStack {
                            Image(systemName: "waveform")
                                .foregroundColor(.blue)
                                .frame(width: 24)
                            Text("Audio Quality")
                        }
                    }

                    NavigationLink {
                        PlaceholderSettingView(title: "Transcription Model")
                    } label: {
                        HStack {
                            Image(systemName: "cpu")
                                .foregroundColor(.blue)
                                .frame(width: 24)
                            Text("Transcription Model")
                        }
                    }
                } header: {
                    Text("Recording")
                }

                Section {
                    NavigationLink {
                        PlaceholderSettingView(title: "Storage Management")
                    } label: {
                        HStack {
                            Image(systemName: "internaldrive")
                                .foregroundColor(.blue)
                                .frame(width: 24)
                            Text("Storage Management")
                        }
                    }

                    NavigationLink {
                        PlaceholderSettingView(title: "Export Options")
                    } label: {
                        HStack {
                            Image(systemName: "square.and.arrow.up")
                                .foregroundColor(.blue)
                                .frame(width: 24)
                            Text("Export Options")
                        }
                    }
                } header: {
                    Text("Data")
                }

                Section {
                    NavigationLink {
                        PlaceholderSettingView(title: "Privacy")
                    } label: {
                        HStack {
                            Image(systemName: "lock.shield")
                                .foregroundColor(.blue)
                                .frame(width: 24)
                            Text("Privacy")
                        }
                    }

                    NavigationLink {
                        PlaceholderSettingView(title: "Notifications")
                    } label: {
                        HStack {
                            Image(systemName: "bell")
                                .foregroundColor(.blue)
                                .frame(width: 24)
                            Text("Notifications")
                        }
                    }
                } header: {
                    Text("Preferences")
                }

                Section {
                    HStack {
                        Text("Version")
                            .foregroundColor(.gray)
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.gray)
                    }
                } header: {
                    Text("About")
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - Appearance Mode

enum AppearanceMode: String, CaseIterable {
    case light = "light"
    case dark = "dark"
    case system = "system"

    var displayName: String {
        switch self {
        case .light: return "Light"
        case .dark: return "Dark"
        case .system: return "System"
        }
    }

    var colorScheme: ColorScheme? {
        switch self {
        case .light: return .light
        case .dark: return .dark
        case .system: return nil
        }
    }
}

// MARK: - Placeholder Settings View

struct PlaceholderSettingView: View {
    let title: String

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "gearshape.2")
                .font(.system(size: 60))
                .foregroundColor(.gray.opacity(0.5))

            Text("\(title)")
                .font(.title2)
                .bold()

            Text("This setting will be available in a future update")
                .font(.subheadline)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(.systemGroupedBackground))
        .navigationTitle(title)
    }
}

#Preview {
    SettingsView()
}
