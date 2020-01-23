function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
    $.ajax({
        url: "api/session",
        type: "DELETE",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        dataType: "json",
        success: function (resp) {
            if (resp.errno == "0") {
                self.location.href = "/index.html";
            }
        }
    })
}

$(document).ready(function(){

    // 查询个人信息
    $.ajax({
        url: "api/user/info",
        type: "get",
        success: function (resp) {
            if (resp.errno == "0") {
                $("#user-name").html(resp.data.name);
                $("#user-mobile").html(resp.data.mobile);
                $("#user-avatar").attr("src", "/api/user/show/" + resp.data.avatar_url)
            } else {
                alert(resp.errmsg);
            }
        }
    });
});