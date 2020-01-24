function hrefBack() {
    history.go(-1);
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

window.onload = function() {
    var mySwiper = new Swiper ('.swiper-container', {
        loop: true,
        autoplay: 2000,
        autoplayDisableOnInteraction: false,
        pagination: '.swiper-pagination',
        paginationType: 'fraction',
        observer: true,
        observeParents:true,
    });
};


$(document).ready(function(){
    var queryData = decodeQuery();
    var houseId = queryData['id'];

    $.ajax({
        url: 'api/detail/' + houseId,
        type: "get",
        success: function (resp) {
            if (resp.errno == "0") {
                var json_data = JSON.parse(resp.data.house_data);
                $(".swiper-container").html(template("house-image-tmpl",{"img_urls": json_data.img_urls, "price": json_data.price} ));
                $(".detail-con").html(template("house-detail-tmpl", {"house": json_data}));

                if (resp.data.user_id != resp.data.house_data.user_id) {
                    $(".book-house").attr("href", "/booking.html?hid=" + json_data.house_id);
                    $(".book-house").show();
                }
            }
        }
    });

});