from views import db, User, Post, Tag, Page
from werkzeug.security import generate_password_hash

db.drop_all()
db.create_all()

admin = User(username='admin', email='amin', password=generate_password_hash('admin'))
db.session.add(admin)
db.session.commit()

python_tag = Tag(name='Python')
web_tag = Tag(name='Web')
db.session.add(python_tag)
db.session.add(web_tag)
db.session.commit()

post1 = Post(
    title="Le Python c'est sympa", 
    slug='le-python-c-est-sympa',
    abstract_image="http://placekitten.com/400/300",
    abstract="Franchement, oui, on peut dire que le python c'est pas mal du tout. Lol. Aller @+ pour de nouvelles aventures !",
    content="Contrairement à une opinion répandue, le Lorem Ipsum n'est pas simplement du texte aléatoire. Il trouve ses racines dans une oeuvre de la littérature latine classique datant de 45 av. J.-C., le rendant vieux de 2000 ans. Un professeur du Hampden-Sydney College, en Virginie, s'est intéressé à un des mots latins les plus obscurs, consectetur, extrait d'un passage du Lorem Ipsum, et en étudiant tous les usages de ce mot dans la littérature classique, découvrit la source incontestable du Lorem Ipsum. Il provient en fait des sections 1.10.32 et 1.10.33 du  (Des Suprêmes Biens et des Suprêmes Maux) de Cicéron. Cet ouvrage, très populaire pendant la Renaissance, est un traité sur la théorie de l'éthique. Les premières lignes du Lorem Ipsumproviennent de la section 1.10.32.L'extrait standard de Lorem Ipsum utilisé depuis le XVIè siècle est reproduit ci-dessous pour les curieux. Les sections 1.10.32 et 1.10.33 du Cicéron sont aussi reproduites dans leur version originale, accompagnée de la traduction anglaise de H. Rackham (1914).",
    user_id=admin.id,
    published=True,
)
post2 = Post(
    title="Le python me rend ZINZIN", 
    slug='le-python-me-rend-zinzin',
    abstract_image="http://placekitten.com/400/300",
    abstract="Franchement, oui, on peut dire que le python me rend ZINZIN. Lol. Aller @+ pour de nouvelles aventures !",
    content="Il trouve ses racines dans une oeuvre de la littérature latine classique datant de 45 av. J.-C., le rendant vieux de 2000 ans. Un professeur du Hampden-Sydney College, en Virginie, s'est intéressé à un des mots latins les plus obscurs, consectetur, extrait d'un passage du Lorem Ipsum, et en étudiant tous les usages de ce mot dans la littérature classique, découvrit la source incontestable du Lorem Ipsum. Il provient en fait des sections 1.10.32 et 1.10.33 du  (Des Suprêmes Biens et des Suprêmes Maux) de Cicéron. Cet ouvrage, très populaire pendant la Renaissance, est un traité sur la théorie de l'éthique. Les premières lignes du Lorem Ipsumproviennent de la section 1.10.32.L'extrait standard de Lorem Ipsum utilisé depuis le XVIè siècle est reproduit ci-dessous pour les curieux. Les sections 1.10.32 et 1.10.33 du Cicéron sont aussi reproduites dans leur version originale, accompagnée de la traduction anglaise de H. Rackham (1914).",
    user_id=admin.id,
    published=True,
)
post1.tags.append(python_tag)
post2.tags.append(python_tag)
post2.tags.append(web_tag)
db.session.add(post1)
db.session.add(post2)
db.session.commit()

page = Page(
    title="La passion du poulet",
    nav_label="Poulet",
    slug="la-passion-du-poulet",
    content="<p>Le poulet cest trop bien</p><p>Ca pond des oeufs!</p>",
    published=True,
)
db.session.add(page)
db.session.commit()

print('Database initialized')