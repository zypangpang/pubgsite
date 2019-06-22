$(function () {
    let selected_user='';
    $('#adduser_btn').click(function () {
       $('#adduser_modal').modal();
    });

    $('#password_check').click(function () {
        if($(this).is(':checked'))
            $('#pwd').attr('type','text');
        else
            $('#pwd').attr('type','password');
    });
    $('#new_password_check').click(function () {
        if($(this).is(':checked'))
            $('#newpwd').attr('type','text');
        else
            $('#newpwd').attr('type','password');
    });
    $('#table_content tr').click(function () {
        $('#table_content tr').removeClass('bg-warning');
        $(this).addClass('bg-warning');
        $("#auth-btn").removeAttr('disabled');
        selected_user=$(this).attr('username');
       /*let index=$('#table_content tr').index(this);
       $('input[type="radio"]').removeAttr('checked');
       $('#user_radio_'+index).attr('checked','checked');
       $("#auth-btn").removeAttr('disabled');*/
    });
    $('#del-btn').click(function () {
        //let username=$('input[type="radio"]:checked').val();
        $('#usr').val(selected_user);
        $('#del-username').text(selected_user);
        $("#delModal").modal();
    });
    /*$('#del_confirm_btn').click(function () {
       $('#delform').submit();
    });*/
    $('#changepwd-btn').click(function () {
        $('#changepwd-usr-input').val(selected_user) ;
        $('#changepwd-username').text("修改 "+selected_user +" 的密码");
       $('#changepwd_modal').modal();
    });
    $('#changegroup-btn').click(function () {
        $("#changegroup-usr-input").val(selected_user);
       $('#changegroup-title').text("修改 "+selected_user+" 所属的用户组");
        $('#changegroup-modal').modal();
    });
    /*$('#changepwd-confirm-btn').click(function () {
        $('#changepwd-form').submit();
    });*/
});