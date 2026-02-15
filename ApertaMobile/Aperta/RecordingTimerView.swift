// ABOUTME: Displays elapsed recording time in MM:SS format
// ABOUTME: Updates in real-time during recording

import SwiftUI

struct RecordingTimerView: View {
    let duration: TimeInterval

    private var formattedTime: String {
        let minutes = Int(duration) / 60
        let seconds = Int(duration) % 60
        return String(format: "%02d:%02d", minutes, seconds)
    }

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: "clock.fill")
                .font(.caption)
            Text(formattedTime)
                .font(.system(.body, design: .monospaced))
                .bold()
        }
        .foregroundColor(.primary)
    }
}

#Preview {
    VStack(spacing: 20) {
        RecordingTimerView(duration: 0)
        RecordingTimerView(duration: 65)
        RecordingTimerView(duration: 185)
        RecordingTimerView(duration: 3665)
    }
    .padding()
}
