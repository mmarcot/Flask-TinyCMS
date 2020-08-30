$(document).ready(function(){
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

    // edit posts modal:
    $('.open-edit-post-modal').click(function(){
        var post = $(this).data('post');
        $('#edit-post-modal input[name="post_id"]').val(post.id);
        $('#edit-post-modal input[name="title"]').val(post.title);
        $('#edit-post-modal input[name="slug"]').val(post.slug);
        $('#edit-post-modal input[name="tags"]').val(post.tags_str);
        $('#edit-post-modal textarea[name="abstract"]').val(post.abstract);
        $('#edit-post-modal input[name="abstract_image"]').val(post.abstract_image);
        $('#edit-post-modal input[name="published"]').prop("checked", post.published);
        $('#edit-post-modal textarea[name="content"]').val(post.content);
    });

});