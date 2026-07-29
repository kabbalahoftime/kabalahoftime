import Foundation

/// What the web page hands over. Nothing here is computed natively: the Hebrew
/// calendar, the cycles and the Sefirah hours all live in the page, and a
/// second implementation in Swift would drift from the first.
struct Snapshot: Codable {
    struct Window: Codable {
        let name: String
        let start: Date
        let end: Date
    }
    struct Prayer: Codable {
        let n: Int
        let name: String
        let sefirah: String
        /// Nil for the three Mochin — Keter, Chochmah and Binah have no clock
        /// window, which is why their tags never flash in the app either.
        let start: Date?
    }
    struct Sefirah: Codable {
        let name: String
        let hebrew: String
        let range: String
    }

    let v: Int
    let generatedAt: Date
    let hebrewDate: String
    let gregorianDate: String
    let dayIndicator: String
    let maalotDone: Int
    let prayersDone: Int
    let sefirahNow: Sefirah?
    let windows: [Window]
    let prayers: [Prayer]

    /// The window containing `date`, if any — used by the widget to name the
    /// Sefirah of the hour without recomputing anything.
    func window(at date: Date) -> Window? {
        windows.first { $0.start <= date && date < $0.end }
    }
}

enum SnapshotStore {
    /// Must match the App Group on both targets.
    static let appGroup = "group.com.kabbalahoftime.shared"
    private static let key = "snapshot.v1"

    private static var defaults: UserDefaults? {
        UserDefaults(suiteName: appGroup)
    }

    /// The page emits ISO-8601 with milliseconds, which the plain `.iso8601`
    /// strategy will not parse.
    static func makeDecoder() -> JSONDecoder {
        let decoder = JSONDecoder()
        let withMillis = ISO8601DateFormatter()
        withMillis.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let plain = ISO8601DateFormatter()
        plain.formatOptions = [.withInternetDateTime]
        decoder.dateDecodingStrategy = .custom { decoder in
            let raw = try decoder.singleValueContainer().decode(String.self)
            if let d = withMillis.date(from: raw) ?? plain.date(from: raw) { return d }
            throw DecodingError.dataCorrupted(
                .init(codingPath: decoder.codingPath, debugDescription: "Bad date: \(raw)"))
        }
        return decoder
    }

    static func save(_ data: Data) {
        defaults?.set(data, forKey: key)
    }

    static func load() -> Snapshot? {
        guard let data = defaults?.data(forKey: key) else { return nil }
        return try? makeDecoder().decode(Snapshot.self, from: data)
    }
}
