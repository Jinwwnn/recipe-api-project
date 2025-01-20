"""
Views for the recipe APIs.
"""
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View to manage recipes API."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):  # override get_serializer_class method
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)
    
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data,
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for user owned recipe attributes."""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """View to manage tags API."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """View to manage ingredients API."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
