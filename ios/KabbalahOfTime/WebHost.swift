import SwiftUI
import WebKit
import SafariServices

/// The whole app is this: the site in a WKWebView, with the two things a
/// browser tab cannot do — links out to Safari without losing your place, and
/// pull to refresh.
struct WebHost: UIViewRepresentable {
    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        // Persistent, so localStorage survives between launches: this is where
        // the day's ma'alot, miutim and prayers are kept.
        config.websiteDataStore = .default()
        config.allowsInlineMediaPlayback = true

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.allowsBackForwardNavigationGestures = false
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.backgroundColor = UIColor(red: 0.969, green: 0.949, blue: 0.910, alpha: 1) // #f7f2e8
        webView.isOpaque = false
        context.coordinator.webView = webView

        let refresh = UIRefreshControl()
        refresh.addTarget(context.coordinator,
                          action: #selector(Coordinator.reload(_:)),
                          for: .valueChanged)
        webView.scrollView.refreshControl = refresh

        webView.load(URLRequest(url: Site.liveURL))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}

    final class Coordinator: NSObject, WKNavigationDelegate {
        weak var webView: WKWebView?
        private var didFallBack = false

        @objc func reload(_ sender: UIRefreshControl) {
            webView?.load(URLRequest(url: Site.liveURL))
        }

        func webView(_ webView: WKWebView,
                     decidePolicyFor navigationAction: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = navigationAction.request.url else {
                decisionHandler(.allow); return
            }
            // Only a tap should leave the app; redirects and sub-frames load in place.
            let isTap = navigationAction.navigationType == .linkActivated
            if isTap, !Site.isOwnHost(url), url.scheme == "https" || url.scheme == "http" {
                present(url)
                decisionHandler(.cancel)
                return
            }
            decisionHandler(.allow)
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            webView.scrollView.refreshControl?.endRefreshing()
        }

        func webView(_ webView: WKWebView,
                     didFail navigation: WKNavigation!, withError error: Error) {
            fallBackIfNeeded(webView, error)
        }

        func webView(_ webView: WKWebView,
                     didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            fallBackIfNeeded(webView, error)
        }

        /// A first launch with no network, before the service worker exists.
        /// Only once — a later failure means the site is momentarily unreachable
        /// and the service worker will answer.
        private func fallBackIfNeeded(_ webView: WKWebView, _ error: Error) {
            webView.scrollView.refreshControl?.endRefreshing()
            guard !didFallBack, let bundled = Site.bundledURL else { return }
            didFallBack = true
            webView.loadFileURL(bundled, allowingReadAccessTo: bundled.deletingLastPathComponent())
        }

        private func present(_ url: URL) {
            guard let scene = UIApplication.shared.connectedScenes
                    .first(where: { $0.activationState == .foregroundActive }) as? UIWindowScene,
                  let root = scene.keyWindow?.rootViewController else { return }
            let safari = SFSafariViewController(url: url)
            safari.preferredControlTintColor = UIColor(red: 0.545, green: 0.412, blue: 0.078, alpha: 1) // #8b6914
            root.present(safari, animated: true)
        }
    }
}
