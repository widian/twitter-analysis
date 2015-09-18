var client = new Keen({
  projectId: "55f93f85d2eaaa05a699de39",
  readKey: "2f1b89a70f545caaeff7964b5daa60236844aa0291a20749e15ca83e30c63d3cb939d7eb720666c03164403680d77d8e6086e3f1d60b5a34f696b09fc1bd695a0a0f0a1f947757cd5bd5666d5448b614e9928a544bfcecfe4bb9e52b1c02d77e49e359c04dc2dd901764097364b00573"
});

Keen.ready(function(){
  // ----------------------------------------
  // Pageviews Area Chart
  // ----------------------------------------
  var pageviews_timeline = new Keen.Query("maximum", {
    eventCollection: "cindemas",
    target_property: "count",
    groupBy: "캐릭터",
    interval: "daily",
    timeframe: "this_14_days"
  });
  client.draw(pageviews_timeline, document.getElementById("main-chart-1"), {
    chartType: "linechart",
    title: false,
    height: 240,
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

$(document).ready(function() {
    $(document).ajaxStart(function () {
        $('div.loading').show();
    });
    $('button.btn-character').on('click', function(e) {
        var char_id = $(this).attr("data-char-id") - 1;
        var collection_id = $(this).parent().attr('data-collection-id') - 1;
        $.ajax({
            url : "api/get_twit",
            data : {
                "character" : char_id,
                "collection" : collection_id
            }
        })
        .done(function (e) {
            var result = $.parseJSON(e);
            if(result["result"]["result"]) {
                Toast.show({
                    message : "데이터를 갱신했습니다. 3초후 새로고침합니다" 
                });
                setTimeout(function () {
                    location.reload(true);
                }, 3000);
            } else {
                switch (result["status"]["code"]){
                    case 429:
                        // reached twitter rate limit
                        var ttl = result["result"]["ttl"];
                        Toast.show({
                            message : "단시간에 너무 많은 요청을 보냈습니다. " + ttl + "초 기다려주세요",
                            background : "#FF3300",
                            position : Toast.POSITION_TOP
                        })
                        break;
                    case 1001:
                        // already refreshed event
                        Toast.show({
                            message : "다른 누군가가 정보를 갱신중입니다. 조금 기다려주세요",
                            background : "#FF3300",
                            position : Toast.POSITION_TOP
                        });
                        break;
                    case 1002:
                        // on refreshing twitter search
                        var ttl = result["result"]["ttl"];
                        Toast.show({
                            message : "오늘의 정보가 갱신되었습니다. 내일 정보는 " + ttl + "초 기다려주세요",
                            background : "#FF3300",
                            position : Toast.POSITION_TOP
                        })
                        break;
                    case 1003:
                        // uncaught required parameters
                        Toast.show({
                            message : "적절하지 못한 파라미터 조합",
                            background : "#FF3300",
                            position : Toast.POSITION_TOP
                        })
                        break;
                    case 500:
                    default:
                        // Unknown
                        Toast.show({
                            message : "알수 없는 에러 발생. 트위터 에러일 가능성이 높습니다",
                            background : "#FF3300",
                            position : Toast.POSITION_TOP
                        })
                        break;
                }
            }
        });
    });
});
