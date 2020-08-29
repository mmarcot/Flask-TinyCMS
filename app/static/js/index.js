$(document).ready(function(){
    // edit tags modal :
    $(".open-edit-tag-modal").click(function(){
        var tag_id = $(this).data('id');
        var tag_name = $(this).data('name');
        $('.modal-body #input-tag-id').val(tag_id);
        $('.modal-body #input-tag-name').val(tag_name);
    });

    // edit users modal:
    $('.open-edit-user-modal').click(function(){
        var user = $(this).data('user');
        $('#input-user-id').val(user.id);
        $('#input-user-username').val(user.username);
        $('#input-user-email').val(user.email);
        $('#input-user-password').val('********');
    });
});