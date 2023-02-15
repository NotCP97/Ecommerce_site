from .serializers import *
from django.http import HttpResponse,JsonResponse,HttpRequest
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics,filters
import os
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import QueryDict
from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from rest_framework import viewsets,views
# Create your views here.


@api_view(["GET"])
def hello(request):
    return JsonResponse({"helolo":"sjdvnjn"})



@api_view(["POST"])
def registration(request):
    print(request.data)
    serializers = UserSerializer(data=request.data)
    if serializers.is_valid():
        serializers.save()
        return Response({"error": False, "message": f"user is created for '{serializers.data['username']}' ",
                             "data": serializers.data})
    return Response({"error": True, "message": serializers.errors, "status": status.HTTP_400_BAD_REQUEST})



@api_view(["POST"])
def createproduct(request):
    print(request.data)
    serializers = ProductSerializers(data=request.data)
    print(serializers.is_valid())
    if serializers.is_valid():
        serializers.save()
        return Response({"error": False, "message": "dnnvj",
                                "data": serializers.data})
    else:
        Response({"error": True, "message": serializers.errors, "status": status.HTTP_400_BAD_REQUEST})



@api_view(["GET"])
def getproduct(request,pk):
    
    product = Product.objects.get(pk = pk)
    serializers = ProductSerializers(product)
    return JsonResponse(serializers.data)
    



@api_view(["DELETE"])
def deleteproduct(request,pk):
    product = Product.objects.get(pk = pk)

    
    return JsonResponse({"hdgh":product.delete()})


@api_view(["GET"])
def listproducts(request):
    products = Product.objects.all()
    # filters = eval(request.GET.get("filters"))
    # print(filters)

    # Direct_Filters = ["id","title","category","selling_price__gte","selling_price__lte"]
    # Indirect_Filters = []


    # direct_Filters = {k:v for k,v in filters.items() if k in Direct_Filters}
    # indirect_Filters = {k:v for k,v in filters.items() if k in Indirect_Filters}

    # products = products.filter(**direct_Filters)

    # print(products.query)

    # for k,v in indirect_Filters.items:
    #     products = eval("apply_"+k+"filter"+f'{products}')





    serializers = ProductSerializers(products,many = True)

    return Response(serializers.data)











@api_view(["PUT"])
def updateproduct(request,pk):
    product = Product.objects.get(pk = pk)
    serializers = ProductSerializers(instance = product,data=request.data)
    if serializers.is_valid():
        serializers.save()
        return Response({"error": False, "message": "deleted",
                                "data": serializers.data})
    else:
        Response({"error": True, "message": serializers.errors, "status": status.HTTP_400_BAD_REQUEST})


@api_view(["POST"])
def createcategory(request):
    print(request.data)
    serializers = CategorySerializer(data=request.data)
    if serializers.is_valid():
        serializers.save()
        return Response({"error": False, "message": "dnnvj",
                                "data": serializers.data})
    else:
        Response({"error": True, "message": serializers.errors, "status": status.HTTP_400_BAD_REQUEST})



@permission_classes([IsAuthenticated])
@permission_classes([TokenAuthentication])
@api_view(["GET"])
def profile(request):
        try:
            query = Profile.objects.get(user=request.user)
            serializer = ProfileSerializers(query)
            response_message = {"error": False, "data": serializer.data}
        except Exception as e:
            print(e)
            response_message = {"error": True, "message": "Something went Wrong"}
        return Response(response_message)


@permission_classes([IsAuthenticated])
@permission_classes([TokenAuthentication])
@api_view(["POST"])
def addtocart(request):
        product_id = request.data['id']
        product_obj = Product.objects.get(id=product_id)
        incomplete_cart = Cart.objects.filter(customer=request.user.profile).filter(complete=False).first()
        try:
            if incomplete_cart:
                this_product_in_cart = incomplete_cart.cartproduct_set.filter(product=product_obj)
                if this_product_in_cart.exists():
                    cart_product = CartProduct.objects.filter(product=product_obj).filter(cart__complete=False).first()
                    cart_product.quantity += 1
                    cart_product.subtotal += product_obj.selling_price
                    cart_product.save()
                    incomplete_cart.total += product_obj.selling_price
                    incomplete_cart.save()
                else:
                    new_cart_product = CartProduct.objects.create(
                        cart=incomplete_cart,
                        price=product_obj.selling_price,
                        quantity=1,
                        subtotal=product_obj.selling_price
                    )
                    new_cart_product.product.add(product_obj)
                    incomplete_cart.total += product_obj.selling_price
                    incomplete_cart.save()
            else:
                Cart.objects.create(customer=request.user.profile, total=0, complete=False)
                new_cart = Cart.objects.filter(customer=request.user.profile).filter(complete=False).first()
                new_cart_product = CartProduct.objects.create(
                    cart=new_cart,
                    price=product_obj.selling_price,
                    quantity=1,
                    subtotal=product_obj.selling_price
                )
                new_cart_product.product.add(product_obj)
                new_cart.total += product_obj.selling_price
                new_cart.save()

            message = {'error': False, 'message': "Product added to Cart", "productid": product_id}

        except Exception as e:
            print(e)
            message = {'error': True, 'message': "Product Not added to Cart! Something went Wrong"}

        return JsonResponse(message)



@permission_classes([IsAuthenticated])
@permission_classes([TokenAuthentication])
@api_view(["GET"])
def showcart(request):
        print(request.user)
        query = Cart.objects.filter(customer=request.user.profile)
        serializers = CartSerializer(query, many=True)
        all_data = []
        for cart in serializers.data:
            cart_product = CartProduct.objects.filter(cart=cart["id"])
            cart_product_serializer = CartProductSerializer(cart_product, many=True)
            cart["cart_product"] = cart_product_serializer.data
            all_data.append(cart)
        return JsonResponse(all_data,safe=False)

@api_view(["PUT"])
def editcartproduct(request):
        cp_obj = CartProduct.objects.get(id=request.data["id"])
        cart_obj = cp_obj.cart

        cp_obj.quantity -= 1
        cp_obj.subtotal -= cp_obj.price
        cp_obj.save()

        cart_obj.total -= cp_obj.price
        cart_obj.save()
        if cp_obj.quantity == 0:
            cp_obj.delete()
        return JsonResponse({"message": "CartProduct Add Update", "product": request.data['id']})



@api_view(["DELETE"])
def deletecartproduct(request):
        cp_obj = CartProduct.objects.get(id=request.data['id'])
        cp_obj.delete()
        return JsonResponse({"message": "CartProduct Deleted", "product": request.data['id']})

@api_view(["DELETE"])
def deletefullcart(self, request):
        try:
            card_obj = Cart.objects.get(id=request.data['id'])
            card_obj.delete()
            message = {"message": "Cart Deleted"}
        except Exception as e:
            print(e)
            message = {"message": "Something went wrong"}
        return JsonResponse(message)


class OrderViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        query = Order.objects.filter(cart__customer=request.user.profile)
        serializers = OrderSerializer(query, many=True)
        all_data = []
        for order in serializers.data:
            cart_product = CartProduct.objects.filter(cart_id=order['cart']['id'])
            cart_product_serializer = CartProductSerializer(cart_product, many=True)
            order['cart_product'] = cart_product_serializer.data
            all_data.append(order)
        return Response(all_data)

    def retrieve(self, request, pk=None):
        try:
            queryset = Order.objects.get(id=pk)
            serializers = OrderSerializer(queryset)
            data = serializers.data
            all_data = []
            cart_product_obj = CartProduct.objects.filter(cart_id=data['cart']['id'])
            cart_product_serializer = CartProductSerializer(cart_product_obj, many=True)
            data['cart_product'] = cart_product_serializer.data
            all_data.append(data)
            message = {"error": False, "data": all_data}
        except Exception as e:
            print(e)
            message = {"error": True, "data": "No data Found for This id"}

        return Response(message)

    def destroy(self, request, pk=None):
        try:
            order_obj = Order.objects.get(id=pk)
            cart_obj = Cart.objects.get(id=order_obj.cart.id)
            order_obj.delete()
            cart_obj.delete()
            message = {"error": False, "message": "Order deleted", "order id": pk}
        except Exception as e:
            print(e)
            message = {"error": True, "message": "Order Not Found"}
        return Response(message)

    def create(self, request):
        print(request.data)
        cart_id = request.data["cartId"]
        cart_obj = Cart.objects.get(id=cart_id)
        address = request.data["address"]
        mobile = request.data["mobile"]
        email = request.data["email"]
        cart_obj.complete = True
        cart_obj.save()
        created_order = Order.objects.create(
            cart=cart_obj,
            address=address,
            mobile=mobile,
            email=email,
            total=cart_obj.total,
            discount=3,
        )

        return Response({"message": "Order Completed", "cart id": cart_id, "order id": created_order.id})


@permission_classes([IsAuthenticated])
@permission_classes([TokenAuthentication])
@api_view(["PUT"])
def updateuser(request):
        try:
            user = request.user
            data = request.data
            user_obj = User.objects.get(username=user)
            user_obj.first_name = data["first_name"]
            user_obj.last_name = data["last_name"]
            user_obj.email = data["email"]
            user_obj.save()
            response_data = {"error": False, "message": "User Data is Updated"}
        except Exception as e:
            print(e)
            response_data = {"error": True, "message": "User Data is not Update Try Again!!!"}
        return Response(response_data)


@permission_classes([IsAuthenticated])
@permission_classes([TokenAuthentication])
@api_view(["PUT"])
def UpdateProfile(request):


 
        try:
            user = request.user
            query = Profile.objects.get(user=user)
            data = request.data
            serializers = ProfileSerializers(query, data=data, context={"request": request})
            serializers.is_valid(raise_exception=True)
            serializers.save()
            return_res = {"message": "Profile is Updated"}
        except Exception as e:
            print(e)
            return_res = {"message": "Something went Wrong Try Again!!!"}
        return Response(return_res)