function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(document).ready(function(){
    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $(".input-daterange").on("changeDate", function(){
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();

        if (startDate && endDate && startDate > endDate) {
            showErrorMsg();
        } else {
            var sd = new Date(startDate);
            var ed = new Date(endDate);
            days = (ed - sd)/(1000*3600*24);
            if (days === 0) {
                days = 1
            }
            var price = $(".house-text>p>span").html();
            var amount = days * parseFloat(price);
            $(".order-amount>span").html(amount.toFixed(2) + "(共"+ days +"晚)");
        }
    });
    $.ajax({
        url: "api/check",
        type: "get",
        success: function (resp) {
            if (resp.errno != "0") {
                self.location.href = "/login.html";
            }
        }
    });

    var queryData = decodeQuery();
    var houseId = queryData["hid"];

    $.ajax({
        url: "/api/detail/" + houseId,
        type: "get",
        success: function (resp) {
            if (resp.errno == "0") {
                var json_data = JSON.parse(resp.data.house_data);
                $(".house-info>img").attr("src", "/api/user/show/"+ json_data.img_urls[0]);
                $(".house-text>h3").html(json_data.title);
                $(".house-text>p>span").html(json_data.price);
            }
        }
    });

    // 提交订单
    $(".submit-btn").on("click", function (e) {
        if ($(".order-amount>span").html()) {
            $(this).prop("disabled", true);
            var startDate = $("#start-date").val();
            var endDate = $("#end-date").val();
            var data = {
                "house_id": houseId,
                "start_date": startDate,
                "end_date": endDate,
            };
            $.ajax({
                url: "/api/orders",
                type: "post",
                data: JSON.stringify(data),
                contentType: "application/json",
                dataType: "json",
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                success: function (resp) {
                    if (resp.errno == "4101") {
                        self.location.href = "/login.html"
                    } else if (resp.errno == "0") {
                        self.location.href = "/orders.html"
                    } else if (resp.errno == "4105") {
                        showErrorMsg()
                    }
                }
            })
        }
    })
})
