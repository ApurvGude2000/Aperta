// ABOUTME: Real-time waveform visualization displaying audio amplitude as animated bars
// ABOUTME: Shows scrolling bars that represent audio input levels

import SwiftUI

struct WaveformView: View {
    let level: Float
    @State private var samples: [Float] = Array(repeating: 0, count: 50)

    var body: some View {
        HStack(alignment: .center, spacing: 2) {
            ForEach(samples.indices, id: \.self) { index in
                RoundedRectangle(cornerRadius: 2)
                    .fill(Color.blue.opacity(0.7))
                    .frame(width: 4, height: CGFloat(samples[index] * 60 + 4))
            }
        }
        .frame(height: 80)
        .onChange(of: level) { _, newLevel in
            // Shift samples left and add new sample on right
            samples.removeFirst()
            samples.append(newLevel)
        }
    }
}

#Preview {
    VStack {
        WaveformView(level: 0.5)
            .padding()
    }
}
