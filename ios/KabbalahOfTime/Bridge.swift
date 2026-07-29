import Foundation
import WebKit
import WidgetKit

/// Receives the page's snapshot, stores it where the widget can read it, and
/// rewrites the prayer notifications. The app does no calendar arithmetic of
/// its own — it stores and displays what the page computed.
final class Bridge: NSObject, WKScriptMessageHandler {
    static let name = "kotBridge"

    func userContentController(_ controller: WKUserContentController,
                               didReceive message: WKScriptMessage) {
        guard message.name == Bridge.name,
              JSONSerialization.isValidJSONObject(message.body),
              let data = try? JSONSerialization.data(withJSONObject: message.body)
        else { return }

        SnapshotStore.save(data)

        guard let snapshot = try? SnapshotStore.makeDecoder().decode(Snapshot.self, from: data)
        else { return }

        PrayerNotifications.reschedule(from: snapshot)
        WidgetCenter.shared.reloadAllTimelines()
    }
}
