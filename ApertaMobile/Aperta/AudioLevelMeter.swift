// ABOUTME: Visual audio level meter showing real-time input volume
// ABOUTME: Color-coded from green (low) to yellow (medium) to red (high)

import SwiftUI

struct AudioLevelMeter: View {
    let level: Float
    let barCount: Int = 20

    private var fillColor: Color {
        switch level {
        case 0..<0.3:
            return .green
        case 0.3..<0.7:
            return .yellow
        default:
            return .red
        }
    }

    var body: some View {
        HStack(spacing: 2) {
            ForEach(0..<barCount, id: \.self) { index in
                let threshold = Float(index) / Float(barCount)
                RoundedRectangle(cornerRadius: 2)
                    .fill(level > threshold ? fillColor : Color.gray.opacity(0.3))
                    .frame(width: 3, height: 24)
            }
        }
        .animation(.easeOut(duration: 0.1), value: level)
    }
}

#Preview {
    VStack(spaci: 30) {
        AudioLevelMeter(level: 0.2)
        AudioLevelMeter(level: 0.5)
        AudioLevelMeter(level: 0.9)
    }
    .padding()
}
