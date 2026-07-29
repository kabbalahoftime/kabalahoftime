import WidgetKit
import SwiftUI

/// The lock-screen and home-screen widget: the ma'alot moon and its count, the
/// heart of the ten prayers, the Hebrew date and the Sefirah of the hour.
///
/// A widget cannot run a web view, so nothing is computed here either — the
/// app writes the page's snapshot to the shared container and this reads it.
/// The timeline turns over at each Sefirah window boundary, so the hour is
/// always current without the app being opened.

struct Entry: TimelineEntry {
    let date: Date
    let hebrewDate: String
    let sefirah: String
    let sefirahHebrew: String
    let maalot: Int
    let prayers: Int
    let stale: Bool
}

private func entry(from snapshot: Snapshot?, at date: Date) -> Entry {
    guard let s = snapshot else {
        return Entry(date: date, hebrewDate: "—", sefirah: "", sefirahHebrew: "",
                     maalot: 0, prayers: 0, stale: true)
    }
    let window = s.window(at: date)
    // The counts reset with the Jewish day, so a snapshot from a previous day
    // should not keep showing yesterday's ma'alot as though they were today's.
    let stale = !Calendar.current.isDate(s.generatedAt, inSameDayAs: date)
    return Entry(date: date,
                 hebrewDate: s.hebrewDate,
                 sefirah: window?.name ?? s.sefirahNow?.name ?? "",
                 sefirahHebrew: s.sefirahNow?.hebrew ?? "",
                 maalot: stale ? 0 : s.maalotDone,
                 prayers: stale ? 0 : s.prayersDone,
                 stale: stale)
}

struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> Entry {
        Entry(date: Date(), hebrewDate: "ט״ו אָב", sefirah: "Netzach",
              sefirahHebrew: "נֶצַח", maalot: 7, prayers: 4, stale: false)
    }

    func getSnapshot(in context: Context, completion: @escaping (Entry) -> Void) {
        completion(entry(from: SnapshotStore.load(), at: Date()))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> Void) {
        let now = Date()
        let snapshot = SnapshotStore.load()
        var entries = [entry(from: snapshot, at: now)]
        // One entry at each remaining window boundary, so the Sefirah of the
        // hour turns over on its own.
        if let s = snapshot {
            for w in s.windows.sorted(by: { $0.start < $1.start }) where w.start > now {
                entries.append(entry(from: s, at: w.start))
            }
        }
        let next = entries.last.map { $0.date.addingTimeInterval(3600) } ?? now.addingTimeInterval(3600)
        completion(Timeline(entries: entries, policy: .after(next)))
    }
}

struct WidgetView: View {
    @Environment(\.widgetFamily) private var family
    var entry: Entry

    private var gold: Color { Color(red: 0.545, green: 0.412, blue: 0.078) }

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(entry.hebrewDate)
                .font(.system(size: family == .systemSmall ? 15 : 17, weight: .semibold))
                .lineLimit(1)
                .minimumScaleFactor(0.7)
            if !entry.sefirah.isEmpty {
                Text(entry.sefirahHebrew.isEmpty
                     ? entry.sefirah
                     : "\(entry.sefirah) · \(entry.sefirahHebrew)")
                    .font(.system(size: 11))
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }
            Spacer(minLength: 2)
            HStack(spacing: 12) {
                Label("\(entry.maalot)/15", systemImage: "moon.fill")
                Label("\(entry.prayers)/10", systemImage: "heart.fill")
            }
            .font(.system(size: 12, weight: .medium))
            .foregroundStyle(gold)
        }
        .padding(.vertical, 2)
        .containerBackground(for: .widget) { Color(red: 0.969, green: 0.949, blue: 0.910) }
    }
}

@main
struct KabbalahOfTimeWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "KabbalahOfTimeWidget", provider: Provider()) { entry in
            WidgetView(entry: entry)
        }
        .configurationDisplayName("Kabbalah of Time")
        .description("The day, the Sefirah of the hour, and how far the ma'alot and the prayers have come.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
