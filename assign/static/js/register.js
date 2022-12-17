$(document).ready(function(){
    $('#ipact').on('input propertychange', function() {       //input propertychange即实时监控键盘输入包括粘贴
        var act = $.trim($(this).val());                     //获取this，即ipwd的val()值，trim函数的作用是去除空格
        if($(this).val()=="" || act.length==0){
            $("#msg_act").html("<font color='red'>账号不能为空</font>");
            $("#btn_register").attr("disabled",true);   //使按钮无法点击
        }
        else{
            $("#msg_act").html("<font color='red'></font>");
        }
    })
})

$(document).ready(function(){
    $('#ipwd').on('input propertychange', function() {       //input propertychange即实时监控键盘输入包括粘贴
        var pwd = $.trim($(this).val());                     //获取this，即ipwd的val()值，trim函数的作用是去除空格
        var rpwd = $.trim($("#i2pwd").val());
        if($(this).val()=="" || pwd.length==0){
            $("#msg_ipwd").html("<font color='red'>密码不能为空</font>");
            $("#btn_register").attr("disabled",true);   //使按钮无法点击
        }
        else{
            $("#msg_ipwd").html("<font color='red'></font>");  
        }
        if(pwd==rpwd){                                   //相同则提示密码匹配
            $("#msg_pwd").html("<font color='green'>两次密码匹配通过</font>");
            $("#btn_register").attr("disabled",false);   //使按钮无法点击
        }
        else{                                           //不相同则提示密码匹配
            $("#msg_pwd").html("<font color='red'>两次密码不匹配</font>");
            $("#btn_register").attr("disabled",true);
        }
    })
})
 
//由于是两个输入框，所以进行两个输入框的几乎相同的判断
$(document).ready(function(){
    $('#i2pwd').on('input propertychange', function() {
        var pwd = $.trim($(this).val());
        var rpwd = $.trim($("#ipwd").val());
        if($(this).val()=="" || pwd.length==0){
            $("#msg_pwd").html("<font color='red'>请输入密码</font>");
            $("#btn_register").attr("disabled",true);   //使按钮无法点击
        }
        else if(pwd==rpwd){
            $("#msg_pwd").html("<font color='green'>两次密码匹配通过</font>");
            $("#btn_register").attr("disabled",false);
        }else{
            $("#msg_pwd").html("<font color='red'>两次密码不匹配</font>");
            $("#btn_register").attr("disabled",true);
        }
    })
})

//加载页面后锁住注册按钮
window.onload = function() {
    $("#btn_register").attr("disabled",true);   //使按钮无法点击
}

//修正modal弹窗高度不能自适应的问题
$(document).ready(function(){
    $('#btn_register').click(function() {
        $('#myModal').css("top", ($(window).height() - $('#myModal').height()) / 2);
        $('#myModal').modal("show");
    })
})