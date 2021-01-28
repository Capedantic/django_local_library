# Big imports
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import datetime
# Local imports
from catalog.models import Book, Author, BookInstance, Genre
from catalog.forms import RenewBookForm

def index(request):
    """View function for home page of site."""

    #Generates counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    #Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    #The 'all()' is implied by default.
    num_authors = Author.objects.count()

    #Number of visits to this view, as counted in the session variable
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    #Number of books with fiction tag.
    num_gfiction = Genre.objects.filter(name__contains='fiction').count()
    num_bfiction = Book.objects.filter(title__icontains='Fiction').count()

    context = {
    'num_books': num_books,
    'num_instances': num_instances,
    'num_instances_available': num_instances_available,
    'num_authors': num_authors,
    'num_gfiction': num_gfiction,
    'num_bfiction': num_bfiction,
    'num_visits': num_visits,
    }

    #Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to the current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksAllListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to all users."""
    permission_required = 'catalog.can_view_all_loaned'
    model  = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@login_required
@permission_required('catalog.can_view_all_loaned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    permission_required = 'catalog.can_view_all_loaned'
    book_instance = get_object_or_404(BookInstance, pk=pk)

    #If this is a POST requerst then process the Form data
    if request.method == 'POST':
        #Create a form instance and populate it with data from the request (binding)
        form = RenewBookForm(request.POST)
        #Check if the form is valid
        if form.is_valid():
            #Process the data in form.cleaned_data as required (here we just write it back to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            #Redirect to a new URL
            return HttpResponseRedirect (reverse('all-borrowed') )
    #If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_view_all_loaned'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__' #Not recommended (potential security issue)
    permission_required = 'catalog.can_view_all_loaned'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_view_all_loaned'

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_view_all_loaned'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_view_all_loaned'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_view_all_loaned'
