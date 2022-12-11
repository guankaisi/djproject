$(document).ready(function(){
    $('#ipwd').on('input propertychange', function() {       //input propertychange即实时监控键盘输入包括粘贴
        var pwd = $.trim($(this).val());                     //获取this，即ipwd的val()值，trim函数的作用是去除空格
        var rpwd = $.trim($("#i2pwd").val());
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
        if(pwd==rpwd){
            $("#msg_pwd").html("<font color='green'>两次密码匹配通过</font>");
            $("#btn_register").attr("disabled",false);
        }else{
            $("#msg_pwd").html("<font color='red'>两次密码不匹配</font>");
            $("#btn_register").attr("disabled",true);
        }
    })
})

//修正modal弹窗高度不能自适应的问题
$(document).ready(function(){
    $('#btn_register').click(function() {
        $('#myModal').css("top", ($(window).height() - $('#myModal').height()) / 2);
        $('#myModal').modal("show");
    })
})

window.onload=function()
    {
        alert('test');
    }
