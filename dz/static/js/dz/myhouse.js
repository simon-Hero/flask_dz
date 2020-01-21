$(document).ready(function(){
    $.ajax({
        url: "api/users/auth",
        type: "get",
        success: function (resp) {
            if (resp.errno == "4101") {
                self.location.href = "/login.html"
            } else if (resp.errno == "0") {
                if (!(resp.data.real_name && resp.data.id_card)) {
                    $(".auth-warn").show();
                    return
                }
                $.ajax({
                    url: "api/user/houses",
                    type: "get",
                    success: function (resp) {
                        if (resp.errno == "4101") {
                            self.location.href = "/login.html"
                        } else if (resp.errno == "0") {
                            $("#houses-list").html(template("houses-list-tmpl", {houses: resp.data.houses}))
                        } else {
                            $("#houses-list").html(template("houses-list-tmpl", {houses: []}))
                        }
                    }
                })
            }
        }
    });
});