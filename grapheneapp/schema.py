import graphene
from graphene_django.types import DjangoObjectType
from .models import Book
import graphql_jwt

class BookType(DjangoObjectType):
    class Meta:
        model = Book

class Query(graphene.ObjectType):
    all_books = graphene.List(BookType)

    def resolve_all_books(root, info):
        return Book.objects.all()

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

class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)