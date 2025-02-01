from django.shortcuts import render, get_object_or_404
from .models import Book, BookInstance, Author, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from catalog.forms import RenewBookForm, CreateBookModelForm
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

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

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 5

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user).filter(status='o').order_by('due_back')
        )
    
class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 5

    def get_queryset(self):
        return (
            BookInstance.objects.filter(status='o').order_by('due_back')
        )

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today() +datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={
            'renewal_date': proposed_renewal_date
        })
    
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.add_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(reverse('author-detail', kwargs={'pk': self.object.pk}))

@login_required
@permission_required('catalog.add_book', raise_exception=True)
def book_create(request):
    if request.method == 'POST':
        form = CreateBookModelForm(request.POST)

        if form.is_valid():
            new_book = form.save()
            return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': new_book.id}))
    else:
        form = CreateBookModelForm()
    
    context = {
        'form': form
    }
    return render(request, 'catalog/book_create_form.html', context)

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'summary', 'author', 'genre']
    permission_required = 'catalog.change_book'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(reverse('author-detail', kwargs={'pk': self.object.pk}))