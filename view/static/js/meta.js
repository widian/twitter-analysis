!function(){
  var meta = new Keen({
    projectId: "55f93f85d2eaaa05a699de39",
    writeKey: "2f1b89a70f545caaeff7964b5daa60236844aa0291a20749e15ca83e30c63d3cb939d7eb720666c03164403680d77d8e6086e3f1d60b5a34f696b09fc1bd695a0a0f0a1f947757cd5bd5666d5448b614e9928a544bfcecfe4bb9e52b1c02d77e49e359c04dc2dd901764097364b00573"
  });
  meta.addEvent("visits", {
    page: {
      title: document.title,
      host: document.location.host,
      href: document.location.href,
      path: document.location.pathname,
      protocol: document.location.protocol.replace(/:/g, ""),
      query: document.location.search
    },
    visitor: {
      referrer: document.referrer,
      ip_address: "${keen.ip}",
      // tech: {} //^ created by ip_to_geo add-on
      user_agent: "${keen.user_agent}"
      // visitor: {} //^ created by ua_parser add-on
    },
    keen: {
      timestamp: new Date().toISOString(),
      addons: [
        { name:"keen:ip_to_geo", input: { ip:"visitor.ip_address" }, output:"visitor.geo" },
        { name:"keen:ua_parser", input: { ua_string:"visitor.user_agent" }, output:"visitor.tech" }
      ]
    }
  });
  // More data modeling examples here:
  // https://github.com/keenlabs/data-modeling-guide/
}();
