import SwiftUI

@main
struct KabbalahOfTimeApp: App {
    var body: some Scene {
        WindowGroup {
            WebHost()
                .ignoresSafeArea(edges: .bottom)
        }
    }
}
