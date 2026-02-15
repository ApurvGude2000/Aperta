// ABOUTME: Animated pulsing red dot indicator for recording state
// ABOUTME: Shows visual feedback that recording is active

import SwiftUI

struct PulsingRecordIndicator: View {
    @State private var isPulsing = false
    let isRecording: Bool

    var body: some View {
        Circle()
            .fill(Color.red)
            .frame(width: 16, height: 16)
            .shadow(color: .red.opacity(0.5), radius: isPulsing ? 8 : 4)
            .scaleEffect(isPulsing ? 1.2 : 1.0)
            .opacity(isRecording ? 1.0 : 0.0)
            .animation(
                isRecording ? .easeInOut(duration: 0.8).repeatForever(autoreverses: true) : .default,
                value: isPulsing
            )
            .onAppear {
                if isRecording {
                    isPulsing = true
                }
            }
            .onChange(of: isRecording) { _, newValue in
                isPulsing = newValue
            }
    }
}

#Preview {
    VStack(spacing: 40) {
        PulsingRecordIndicator(isRecording: true)
        PulsingRecordIndicator(isRecording: false)
    }
    .padding()
}
