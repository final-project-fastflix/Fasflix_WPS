from django.contrib.auth import authenticate, login
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import ProfileImageCategory
from ..serializer import *


# 회원가입 API
class UserCreate(generics.CreateAPIView):
    """
        계정을 만드는 API 입니다

        ---
            - email : 이메일
            - password : 비밀번호

        return 값은 방금 만든 계정이름과 비밀번호가 리턴됩니다

        요청시 아래와 같이 요청해주시면 됩니다.
        ```
        Body에 email과 password를 넣어서 보내주시면 됩니다
            email : 이메일
            password : 비밀번호
        ```
    """
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)


# 회원가입이 되면 회원가입 완료 시그널을 받아 토큰을 생성하고 저장한다
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# 기본 계정에 대한 서브유저(프로필계정)을 만드는 뷰


class SubUserCreate(APIView):
    """
            서브계정(프로필계정)을 만드는 API입니다

            ---

            Header에
                Authorization : Token 토큰값
            을 넣어주세요!


                - name : 프로필이름
                - kid : 어린이인지? (true/false)

            성공할 경우 계정에 생성된 모든 프로필 계정 목록을 반환합니
            ※ 프로필 이름이 이미 등록되어 있는경우 'error' : 0을 리턴합니다

            요청시 아래와 같이 요청해주시면 됩니다.
            ```
                헤더에 Authorization : Token '토큰값' 을 넣어주세요
                Body에 user와 kid를 넣어서 보내주시면 됩니다

                만약 여러개의 데이터를 넣고싶으신 경우 아래와 같이 보내주시면 됩니다.

                요청1 :
                {
                    "name": ["이름1", "이름2", "이름3", "이름4"]
                    "kid": [false, true, false, false]
                }


                요청2 :
                {
                    "name": ["이름1"]
                    "kid": [false]
                }


                리턴값:

              {
                "sub_user_list": [
                    {
                        "id": 1,
                        "name": "HDS1",
                        "kid": false,
                        "parent_user": 2
                    },
                    {
                        "id": 2,
                        "name": "HDS2",
                        "kid": false,
                        "parent_user": 2
                    },
                    {
                        "id": 5,
                        "name": "HDS3",
                        "kid": true,
                        "parent_user": 2
                    },
                    {
                        "id": 6,
                        "name": "HDS4",
                        "kid": false,
                        "parent_user": 2
                    },
                    {
                        "id": 7,
                        "name": "HDS5",
                        "kid": true,
                        "parent_user": 2
                    }
                ]
              }

                    name : 프로필이름
                    kid : true/false

            ```
        """

    def post(self, request):
        # 프로필계정을 5개를 초과할 수 없음
        # 기존 등록 되어있는 프로필계정의 목록
        sub_user_list = SubUser.objects.filter(parent_user_id=request.user.id)

        if len(sub_user_list) >= 5:
            return Response(data={'error': '프로필을 더이상 만들 수 없습니다.'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        # 바디 형
        username = request.data.get('name')
        kids = request.data.get('kid')

        is_exist = [False, False, False, False, False]
        basic_image_list = ProfileImage.objects.filter(category='basic').order_by('pk')
        sub_user_img_path_list = []

        # 이름을 비교하기 위한 리스트
        # 기존 프로필 계정 목록에서 이름만 가져온 리스트
        sub_user_name_list = []

        index = 0
        for sub_user in sub_user_list:
            sub_user_name_list.append(sub_user.name)
            sub_user_img_path_list.append(sub_user.profile_image_path)
            name_index = ProfileImage.objects.get(image_path=sub_user_img_path_list[index]).name[-1]
            if name_index.isnumeric():
                is_exist[int(name_index) - 1] = True
            index += 1

        # 입력한 username이 여러개인 경우(맨 처음 회원가입 하였을때)
        if isinstance(username, list):
            for index in range(len(username)):

                if username[index] in sub_user_name_list:
                    return Response(data={'error': False}, status=status.HTTP_403_FORBIDDEN)

                serializer = SubUserCreateSerializer(
                    data={
                        'name': username[index],
                        'kid': kids[index],
                    }
                )
                if serializer.is_valid():
                    serializer.save(
                        parent_user=request.user,
                        profile_image_path=basic_image_list[index].image_path,
                    )

                    sub_user_list = SubUser.objects.filter(parent_user_id=request.user.id)
                    sub_user_list_serializer = SubUserListSerializer(sub_user_list, many=True)

            return Response(data={'sub_user_list': sub_user_list_serializer.data}, status=status.HTTP_200_OK)

        # 입력된 username이 1개 인 경우(일반적인 경우)
        else:
            if username in sub_user_name_list:
                return Response(data={'error': False}, status=status.HTTP_400_BAD_REQUEST)

            serializer = SubUserCreateSerializer(
                data={'name': username, 'kid': kids}
            )

            if serializer.is_valid():
                serializer.save(parent_user=request.user,
                                profile_image_path=basic_image_list[is_exist.index(False)].image_path
                                )

                sub_user_list = SubUser.objects.filter(parent_user_id=request.user.id)
                sub_user_list_serializer = SubUserListSerializer(sub_user_list, many=True)
                return Response(data={'sub_user_list': sub_user_list_serializer.data}, status=status.HTTP_200_OK)

            return Response(data={'error': False}, status=status.HTTP_400_BAD_REQUEST)


# 계정에 속한 프로필계정 모두 보여주기
class SubUserList(generics.ListAPIView):
    """
        계정에 속한 모든 프로필을 보여주는 API입니다

        ---
            Header에
                Authorization : Token 토큰값
            을 넣어주세요! (subuserid는 _(언더바)가 없습니다)

            리턴값:
                - id : 프로필 계정의 ID
                - profile_info : {
                    - image_id : 이미지의 고유 ID
                    - profile_image_path : 프로필 이미지의 path
                    }
                - name : 프로필이름
                - kid : 어린이인지? (true/false)
                - is_initialize : true/false
                - parent_user : 속한 계정의 ID값



            return 값은 계정에 속한 모든 프로필을 리턴합니다

            ```
                해당 URL로 Header에
                    Authorization : Token '토큰값' 을 넣어주세요

            ```
        """

    serializer_class = SubUserListSerializer

    def get_queryset(self):
        queryset = SubUser.objects.filter(parent_user_id=self.request.user.id)

        return queryset


class SubUserModify(APIView):
    """

        기존 프로필계정의 정보를 변경하는 API뷰 입니다

        ---
            Header에
                Authrization: Token 토큰값
            Body에
                sub_user_id 와 함께 변경하고자 하는 정보를 넣어주세요
                    *sub_user_id 필수 !!*
                Ex) name : '변경하고싶은 이름'
                    kid : true/false
                    profile_image_path : '프로필 이미지 path'
                중 변경하고자 하는 것만 넣어서 보내주시면 됩니다.
                Ex) name만 보내주거나 name, kid 를 보내주시거나 등등

            리턴값:
                response: False -> 수정 실패
                response: True -> 수정 성공

    """

    serializer_class = SubUserUpdateSerializer

    def get_object(self):
        sub_user_id = self.request.data.get('sub_user_id')
        return SubUser.objects.get(id=sub_user_id)

    def patch(self, request):
        sub_user = self.get_object()
        serializer = SubUserUpdateSerializer(instance=sub_user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'response': True}, status=status.HTTP_200_OK)
        return Response({'response': False}, status=status.HTTP_400_BAD_REQUEST)


# 프로필 계정을 삭제하는 API
class SubUserDelete(APIView):
    """
        기존 프로필계정을 삭제하는 API뷰 입니다

        ---

            Header에
                Authrization: Token 토큰값
                subuserid : 프로필 계정의 ID
            넣어서 보내주세요 (subuserid는 _(언더바)가 없습니다)

            리턴값:
                response: False -> 삭제 실패
                response: True -> 삭제 성공

        ---


    """
    serializer_class = SubUserDeleteSerializer

    def delete(self, request):
        sub_user_id = request.META['HTTP_SUBUSERID']
        sub_user = SubUser.objects.get(id=sub_user_id)
        # 자신이 가지고 있는 프로필계정만 삭제가능
        is_exist_sub_user_list = SubUser.objects.filter(parent_user=request.user).exists()

        if is_exist_sub_user_list:
            sub_user_list = SubUser.objects.filter(parent_user=request.user)
            if sub_user in sub_user_list:
                sub_user.delete()
                return Response({'response': True}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'response': False}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'response': False}, status=status.HTTP_400_BAD_REQUEST)


# 로그인 API뷰
class Login(APIView):
    """
        로그인 API 입니다

        ---
        ```
            Body에 넣어서 보내주시면 됩니다

                id : 가입시 Email입니다
                pw : 비밀번호

            로그인 완료시 해당 계정의 토큰과 계정의 프로필계정 목록을 반환합니다

        리턴값 :

            {
                "sub_user_list": [
                    {
                        "id": 프로필 계정의 ID,
                        "profile_info : {
                            "image_id" : 프로필 이미지 ID
                            "profile_image_path : 프로필 이미지의 path
                        }
                        "name": 프로필 계정명,
                        "kid": true/false,
                        "parent_user": 속한 계정의 ID
                    },
                    ... 프로필 유저의 갯수만큼 나옴
                ]
            }
        ```
    """
    # 로그인은 인증을 받지 않아도 접속가능
    permission_classes = (AllowAny,)

    def post(self, request):
        # 바디 형1 -> request.POST 가능하나 request.data 좀더 유연한 방식이다
        # username = request.POST.get('id')
        # password = request.POST.get('pw')

        # 바디 형2
        username = request.data.get('id')
        password = request.data.get('pw')

        # 해당하는 유저가 있는지 확인
        user = authenticate(username=username, password=password)

        if user is not None:
            # 유저가 로그인 가능한 권한이 있으면 로그인함
            if user.is_active:
                login(request, user)

                # 받은 정보로 토큰을 돌려준다
                user_id = User.objects.get(username=username).id
                token = Token.objects.get(user_id=user_id).key

                sub_user_list = SubUser.objects.filter(parent_user_id=request.user.id)
                sub_user_list_serializer = SubUserListSerializer(sub_user_list, many=True)

                context = {'token': token, 'sub_user_list': sub_user_list_serializer.data}

                return Response(context, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ChangeProfileImageList(APIView):
    """
                프로필사진 변경을 위한 캐릭터사진 리스트 입니다.

            ---

                /accounts/change_profile/  로 요청하시면 됩니다.

            Header에
                Authorization : Token 토큰값
            을 넣어주세요!



                1. 로고 전부
                2. section에 해당하는 캐릭터들

                의 순서로 데이터가 전달됩니다.

    """

    def get(self, request):
        category_list = ProfileImageCategory.objects.all().prefetch_related('profile_images')

        ret = {}

        for category in category_list:
            char_images = category.profile_images.all()
            ret[f'{category.name}'] = ChangeProfileImageSerializer(char_images, many=True).data

        return Response(ret)


class VisitedBaseMovies(APIView):
    """
        해당 서브유저가 생성된 후 영화선택 페이지에 방문했다는 정보를 저장합니다.

        ---

            /accounts/visited_base_movies/  로 요청하시면 됩니다.

            Header에
                Authorization : Token 토큰값
            을 넣어주세요!

            Body에
                sub_user_id : sub_user_id
            를 넣어주세요!

            해당 서브유저가 존재한다면 saved : True
            존재하지 않는다면 404 에러가 반환됩니다.

    """

    def post(self, *args, **kwargs):
        sub_user = get_object_or_404(SubUser, pk=self.request.data.get('sub_user_id'))

        sub_user.is_initialize = True
        sub_user.save()
        return Response({'saved': True})


def add_default(request):
    queryset = SubUser.objects.filter(profile_image_path='')
    for obj in queryset:
        obj.profile_image_path = 'https://occ-0-2794-2219.1.nflxso.net/art/0a23d/bd81473c570e4f6898dae0375550d809c230a23d.png'
        obj.save()

    return HttpResponse({})
