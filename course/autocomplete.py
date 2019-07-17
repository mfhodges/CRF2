

from dal import autocomplete

from django.contrib.auth.models import User



class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        print("self.request.user.is_authenticated",self.request.user.is_authenticated)
        if not self.request.user.is_authenticated:
            return User.objects.none()

        qs = User.objects.all()
        if self.q:
            # lets limit it to only the first 8 matches
            qs = qs.filter(username__istartswith=self.q)[:8]
        else:
            # dont show all of them if there is nothing there
            return User.objects.none()
        return qs

    def get_result_value(self, result):
        """
        this below is the default behavior,
        change it to whatever you want returned
        """
        return str(result.username)




# should have this for subjects,  and potentially content copies
