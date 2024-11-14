import graphene
from graphene_django.types import DjangoObjectType
from .models import Book
import graphql_jwt


class BookType(DjangoObjectType):
    class Meta:
        model = Book


class Query(graphene.ObjectType):
    all_books = graphene.List(BookType, page=graphene.Int(default_value=1), per_page=graphene.Int(default_value=10))
    book = graphene.Field(BookType, id=graphene.Int(required=True))

    def resolve_all_books(root, info, page, per_page):
        return Book.objects.all()[(page - 1) * per_page: page * per_page]

    def resolve_book(root, info, id):
        try:
            return Book.objects.get(pk=id)
        except Book.DoesNotExist:
            return None


class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        author = graphene.String(required=True)
        published_date = graphene.types.datetime.Date(required=True)

    book = graphene.Field(BookType)

    def mutate(self, info, title, author, published_date):
        book = Book(title=title, author=author, published_date=published_date)
        book.save()
        return CreateBook(book=book)


class UpdateBook(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        author = graphene.String()
        published_date = graphene.types.datetime.Date()

    book = graphene.Field(BookType)

    def mutate(self, info, id, title=None, author=None, published_date=None):
        try:
            book = Book.objects.get(pk=id)
        except Book.DoesNotExist:
            return None

        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if published_date is not None:
            book.published_date = published_date

        book.save()
        return UpdateBook(book=book)


class DeleteBook(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            book = Book.objects.get(pk=id)
            book.delete()
            return DeleteBook(success=True)
        except Book.DoesNotExist:
            return DeleteBook(success=False)


class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    update_book = UpdateBook.Field()
    delete_book = DeleteBook.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
