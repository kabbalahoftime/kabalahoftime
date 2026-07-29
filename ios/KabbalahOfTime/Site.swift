import Foundation

/// Where the app gets its content.
///
/// The live site is loaded whenever it can be reached, so a merge to main is
/// on the phone immediately rather than waiting on App Store review — the app
/// updates several times a day. Offline is covered by the site's own service
/// worker, which is network-first for HTML and cache-first for everything
/// else; the bundled copy below is only the cold-start fallback, for a first
/// ever launch with no network before the service worker has installed.
///
/// Loading remotely also keeps the origin stable, which matters more than it
/// looks: the ma'alot, the miutim and the ten prayers all live in
/// localStorage, and localStorage is per-origin. Serving the bundled file
/// instead would give a different origin and a different, empty store.
enum Site {
    static let liveURL = URL(string: "https://www.reflectionsofitall.com/")!

    /// The copy that ships inside the app, for a first launch with no network.
    static var bundledURL: URL? {
        Bundle.main.url(forResource: "index", withExtension: "html")
    }

    /// Hosts the app itself renders. Anything else — Sefaria, HebrewBooks,
    /// Chabad.org, the recordings — opens in Safari rather than navigating the
    /// app away from the day's page.
    static func isOwnHost(_ url: URL) -> Bool {
        guard let host = url.host?.lowercased() else { return false }
        return host == "reflectionsofitall.com"
            || host == "www.reflectionsofitall.com"
    }
}
