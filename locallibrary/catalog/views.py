from django.shortcuts import render
from .models import Book, BookInstance, Author, Genre
from django.views import generic

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()

    num_genres = Genre.objects.count()
    word = '19'
    num_books_contain = Book.objects.filter(title__icontains=word).count()

    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'word': word,
        'num_books_contain': num_books_contain,
        'num_visits': num_visits,
    }

    return render(request, 'catalog/index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'
    template_name = 'books/book_list.html'
    paginate_by = 5

    def get_queryset(self):
        return Book.objects.all()[:10]
    
class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5

    def get_queryset(self):
        return Author.objects.all()[:10]
    
class AuthorDetailView(generic.DetailView):
    model = Author