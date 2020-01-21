//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);

    $.ajax({
        url: "api/orders?role=custom",
        type: "get",
        success: function (resp) {
            if (resp.errno == "0") {
                $(".orders-list").html(template("orders-list-temp", {orders: resp.data.orders}));
                $(".order-pay").on("click", function (e) {
                    var orderId = $(this).parents("li").attr("order-id");
                    $.ajax({
                        url: "api/orders/" + orderId + "/payment",
                        type: "post",
                        dataType: "json",
                        headers: {
                            "X-CSRFToken": getCookie("csrf_token")
                        },
                        success: function (resp) {
                            if (resp.errno == "4101") {
                                self.location.href = "/login.html"
                            } else if (resp.errno == "0") {
                                self.location.href = resp.data.pay_url
                            }
                        }
                    });

                });
                $(".order-comment").on("click", function(){
                    var orderId = $(this).parents("li").attr("order-id");
                    $(".modal-comment").attr("order-id", orderId);
                });
                $(".modal-comment").on("click", function () {
                    var orderId = $(this).attr("order-id");
                    var comment = $("#comment").val();
                    if (!comment) return;
                    var data = {
                        order_id: orderId,
                        comment: comment
                    };
                    $.ajax({
                        url: "api/orders/" + orderId + "/comment",
                        type: "PUT",
                        data: JSON.stringify(data),
                        dataType: "json",
                        contentType: "application/json",
                        headers: {
                            "X-CSRFToken": getCookie("csrf_token")
                        },
                        success: function (resp) {
                            if (resp.errno == "4101") {
                                self.location.href = "/login.html"
                            } else if (resp.errno == "0") {
                                $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("已完成");
                                $("ul.orders-list>li[order-id="+ orderId +"]>div.order-title>div.order-operate").hide();
                                $("#comment-modal").modal("hide");
                            }
                        }
                    });

                })
            }
        }
    });


});