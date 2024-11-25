import graphene
from graphene_django.types import DjangoObjectType
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from .models import Book, Author
import graphql_jwt

# Define the Author and Book types
class AuthorType(DjangoObjectType):
    class Meta:
        model = Author
        interfaces = (relay.Node,)

class BookType(DjangoObjectType):
    class Meta:
        model = Book
        interfaces = (relay.Node,)

# Define the filter and connection fields
class Query(graphene.ObjectType):
    all_books = DjangoFilterConnectionField(BookType)
    all_authors = DjangoFilterConnectionField(AuthorType)
    author = relay.Node.Field(AuthorType)
    book = relay.Node.Field(BookType)

    def resolve_all_books(self, info, **kwargs):
        return Book.objects.all()

    def resolve_all_authors(self, info, **kwargs):
        return Author.objects.all()

    def resolve_author(self, info, id):
        try:
            return Author.objects.get(pk=id)
        except Author.DoesNotExist:
            return None

    def resolve_book(self, info, id):
        try:
            return Book.objects.get(pk=id)
        except Book.DoesNotExist:
            return None

# Mutation class to handle create, update, and delete operations for Book and Author
class CreateAuthor(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        birth_date = graphene.types.datetime.Date(required=True)

    author = graphene.Field(AuthorType)

    def mutate(self, info, name, birth_date):
        author = Author(name=name, birth_date=birth_date)
        author.save()
        return CreateAuthor(author=author)


class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        author_id = graphene.Int(required=True)
        published_date = graphene.types.datetime.Date(required=True)

    book = graphene.Field(BookType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, title, author_id, published_date):
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            raise Exception('Author not found')

        # Book creation
        book = Book(title=title, author=author, published_date=published_date)
        book.save()
        return CreateBook(book=book, success=True, errors=[])


class UpdateBook(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        author = graphene.Int()
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
            book.author_id = author
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


# Mutation class to handle JWT authentication
class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    create_author = CreateAuthor.Field()
    update_book = UpdateBook.Field()
    delete_book = DeleteBook.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


# Schema definition
schema = graphene.Schema(query=Query, mutation=Mutation)
