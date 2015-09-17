var client = new Keen({
  projectId: "55f93f85d2eaaa05a699de39",
  readKey: "2f1b89a70f545caaeff7964b5daa60236844aa0291a20749e15ca83e30c63d3cb939d7eb720666c03164403680d77d8e6086e3f1d60b5a34f696b09fc1bd695a0a0f0a1f947757cd5bd5666d5448b614e9928a544bfcecfe4bb9e52b1c02d77e49e359c04dc2dd901764097364b00573"
});

Keen.ready(function(){
  // ----------------------------------------
  // Pageviews Area Chart
  // ----------------------------------------
  var pageviews_timeline = new Keen.Query("maximum", {
    eventCollection: "test_cases",
    target_property: "count",
    groupBy: "user_name",
    interval: "daily",
    timeframe: "this_7_days"
  });
  client.draw(pageviews_timeline, document.getElementById("main-chart"), {
    chartType: "areachart",
    title: false,
    height: 250,
    width: "auto",
    chartOptions: {
      chartArea: {
        height: "85%",
        left: "5%",
        top: "5%",
        width: "80%"
      },
      isStacked: false 
    }
  });
});
