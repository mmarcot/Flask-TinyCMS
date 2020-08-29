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

    // edit pages modal:
    $('.open-edit-page-modal').click(function(){
        var page = $(this).data('page');
        $('#modal-edit-page input[name="page_id"]').val(page.id);
        $('#modal-edit-page input[name="title"]').val(page.title);
        $('#modal-edit-page input[name="nav_label"]').val(page.nav_label);
        $('#modal-edit-page input[name="slug"]').val(page.slug);
        $('#modal-edit-page input[name="published"]').prop("checked", page.published);
        $('#modal-edit-page textarea[name="content"]').val(page.content);
    });
});