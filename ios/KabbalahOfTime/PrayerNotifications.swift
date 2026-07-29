import Foundation
import UserNotifications

/// A notification when each prayer's Sefirah hour opens — the flashing tag on
/// the card, reaching you with the app closed.
///
/// Only seven of the ten are scheduled: Hitbodedut, Tikkun Rachel and Tikkun
/// Leah belong to the three Mochin, which have no clock window, exactly as in
/// the app. Triggers repeat daily and are rewritten whenever the app runs, so
/// sha'ot zmaniyot — which drift a few minutes a day — stay close.
enum PrayerNotifications {
    private static let prefix = "kot.prayer."

    static func requestAuthorization() {
        UNUserNotificationCenter.current()
            .requestAuthorization(options: [.alert, .sound]) { _, _ in }
    }

    static func reschedule(from snapshot: Snapshot) {
        let center = UNUserNotificationCenter.current()
        center.getPendingNotificationRequests { pending in
            let ours = pending.map(\.identifier).filter { $0.hasPrefix(prefix) }
            center.removePendingNotificationRequests(withIdentifiers: ours)

            var calendar = Calendar(identifier: .gregorian)
            calendar.timeZone = .current

            for prayer in snapshot.prayers {
                guard let start = prayer.start else { continue }
                let parts = calendar.dateComponents([.hour, .minute], from: start)
                guard let hour = parts.hour, let minute = parts.minute else { continue }

                let content = UNMutableNotificationContent()
                content.title = prayer.name
                content.body  = "\(prayer.sefirah) — the hour has come"
                content.sound = .default
                content.threadIdentifier = "kot.prayers"

                var when = DateComponents()
                when.hour = hour
                when.minute = minute

                center.add(UNNotificationRequest(
                    identifier: prefix + String(prayer.n),
                    content: content,
                    trigger: UNCalendarNotificationTrigger(dateMatching: when, repeats: true)
                ))
            }
        }
    }
}
