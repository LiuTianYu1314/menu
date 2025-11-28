import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from . import settings
from .models import Delicious, Psw, Time
from datetime import datetime, date
from django.utils import timezone


# 创建菜单
@csrf_exempt
def add_delicious(request):
    try:
        # 解析json数据
        data = json.loads(request.body)

        # 创建新菜品
        dish = Delicious.objects.create(
            name=data.get('name'),
            price=data.get('price'),
            src=data.get('src')  # 这里现在可能是 'desktop/neo1.jpg'
        )

        return JsonResponse({
            'success': True,
            'message': '添加成功',
            'id': dish.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'添加失败{str(e)}',
        }, status=400)


# 登录请求
@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    try:
        data = json.loads(request.body)
        account = data.get('account')
        password = data.get('password')

        if account and password:
            return JsonResponse({
                'success': True,
                'message': '登录成功',
                'token': 'mock-jwt-token',
                'user': {
                    'id': 1,
                    'account': 'account'
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '账号不能为空'
            }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '无效请求数据'
        }, status=400)


# 获取所有PSW账号数据
@csrf_exempt
@require_http_methods(["GET"])
def get_psw_data(request):
    try:
        psw_list = Psw.objects.all().values('id', 'account', 'password', 'time')
        data = list(psw_list)

        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取数据失败:{str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_psw_account(request):
    try:
        data = json.loads(request.body)
        account = data.get('account')
        password = data.get('password')

        if not account or not password:
            return JsonResponse({
                'success': False,
                'message': '账号和密码不能为空'
            }, status=400)
        # 创建新账号
        psw_account = Psw.objects.create(
            account=account,
            password=password
        )
        return JsonResponse({
            'success': True,
            'message': '账号添加成功',
            'id': psw_account.id
        }, status=201)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'添加失败:{str(e)}'
        }, status=400)


# 删除PSW账号
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_psw_account(request, account_id):
    try:
        psw_account = Psw.objects.get(id=account_id)
        psw_account.delete()

        return JsonResponse({
            'success': True,
            'message': '账号删除成功'
        })
    except Psw.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '账号不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }, status=500)


# 获取所有菜品数据
@csrf_exempt
@require_http_methods(["GET"])
def get_delicious_data(request):
    try:
        delicious_list = Delicious.objects.all().values('id', 'name', 'price', 'src')
        data = list(delicious_list)
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取菜品数据失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def upload_image(request):
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'message': '没有找到图片文件'
            }, status=400)

        image_file = request.FILES['image']
        filename = request.POST.get('filename', image_file.name)
        current_file_path = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
        img_dir = os.path.join(project_root, 'menu', 'frontend', 'public', 'img')
        os.makedirs(img_dir, exist_ok=True)

        # 保存图片文件
        file_path = os.path.join(img_dir, filename)
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        print(f"图片保存到: {file_path}")  # 添加日志

        return JsonResponse({
            'success': True,
            'message': '图片上传成功',
            'filename': filename
        })

    except Exception as e:
        print(f"上传错误: {str(e)}")  # 添加错误日志
        return JsonResponse({
            'success': False,
            'message': f'图片上传失败: {str(e)}'
        }, status=500)



@csrf_exempt
@require_http_methods(["GET"])
def menu_data(request):
    try:
        menus = Delicious.objects.all().values('id','name','price','src')
        menu_list = list(menus)
        return JsonResponse(menu_list,safe=False)
    except Exception as e:
        return JsonResponse({
            'error':str(e)
        },status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_menu(request,id):
    try:
        menu = Delicious.objects.get(id=id)
        menu.delete()
        return JsonResponse({'success':True})
    except Delicious.DoesNotExist:
        return JsonResponse({'success':'菜单不存在'},status=404)
    except Exception as e:
        return JsonResponse({'error':str(e)},status=500)

# 点赞功能
# 点赞功能
@csrf_exempt
@require_http_methods(["POST"])
def add_like(request):
    try:
        data = json.loads(request.body)
        delicious_id = data.get('delicious_id')
        number = data.get('number', 1)

        # 获取对应的菜品
        delicious = Delicious.objects.get(id=delicious_id)

        # 创建Time记录并关联菜品
        time_record = Time.objects.create(
            number=number,
            delicious=delicious
        )
        return JsonResponse({
            'success': True,
            'message': '点亮成功',
            'time_id': time_record.id
        })
    except Delicious.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '菜品不存在',
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'点亮失败:{str(e)}',
        }, status=500)


# 获取今日菜单
@csrf_exempt
@require_http_methods(["GET"])
def today_menu(request):
    try:
        selected_date = request.GET.get('date')

        if selected_date:
            # 将字符串日期转换为datetime对象
            target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

            # 获取该日期范围内被点赞的菜品
            time_records = Time.objects.filter(
                time__date=target_date
            ).select_related('delicious')

            # 统计每个菜品的点赞数
            menu_items = {}
            for record in time_records:
                delicious = record.delicious
                if delicious.id not in menu_items:
                    menu_items[delicious.id] = {
                        'id': delicious.id,
                        'name': delicious.name,
                        'price': str(delicious.price),
                        'src': delicious.src,
                        'vote_count': 0
                    }
                menu_items[delicious.id]['vote_count'] += record.number

            menu_list = list(menu_items.values())
            return JsonResponse(menu_list, safe=False)
        else:
            return JsonResponse({
                'success': False,
                'message': '请提供日期参数'
            }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取菜单失败: {str(e)}'
        }, status=500)




