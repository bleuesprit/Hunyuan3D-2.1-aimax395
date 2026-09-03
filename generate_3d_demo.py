"""
调用 Hunyuan3D API 生成 3D 模型并保存到家目录
"""
import base64
import os
import sys
import requests

API_URL = "http://localhost:8288"


def image_to_base64(image_path: str) -> str:
    """将图片文件转换为 base64 编码字符串"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_3d_model(image_path: str, texture: bool = True, output_dir: str = None):
    """
    调用 API 生成 3D 模型

    Args:
        image_path: 输入图片路径
        texture: 是否生成纹理（True=生成纹理，False=仅形状）
        output_dir: 输出目录，默认保存到图片所在目录
    """
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(image_path))
        if not output_dir:
            output_dir = "."

    # 检查图片是否存在
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在: {image_path}")
        return

    image_b64 = image_to_base64(image_path)
    image_name = os.path.splitext(os.path.basename(image_path))[0]

    print(f"正在生成 3D 模型... (图片: {image_path}, 纹理: {'是' if texture else '否'})")

    # 构造请求体
    payload = {
        "image": image_b64,
        "remove_background": True,
        "texture": texture,
        "seed": 1234,
        "octree_resolution": 256,
        "num_inference_steps": 5,
        "guidance_scale": 5.0,
        "num_chunks": 8000,
        "face_count": 40000,
    }

    try:
        # 调用同步生成接口
        response = requests.post(
            f"{API_URL}/generate",
            json=payload,
            timeout=6000000,  # 生成可能需要较长时间
        )

        if response.status_code == 200:
            # 保存返回的模型文件
            output_path = os.path.join(output_dir, f"{image_name}_3d.glb")
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✅ 生成成功! 模型已保存到: {output_path}")
        else:
            # 打印错误信息
            print(f"❌ 生成失败 (状态码: {response.status_code})")
            try:
                error_info = response.json()
                print(f"错误详情: {error_info}")
            except Exception:
                print(f"响应内容: {response.text[:500]}")

    except requests.exceptions.Timeout:
        print("❌ 请求超时（生成可能需要更长时间，可以尝试调大 timeout）")
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 API 服务: {API_URL}")
        print("请确保 API 服务已启动: python api_server.py --model_path <模型路径>")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python generate_3d.py <图片路径> [--no-texture]")
        print("示例: python generate_3d.py ~/Pictures/car.png")
        print("      python generate_3d.py ~/Pictures/car.png --no-texture")
        sys.exit(1)

    image_path = sys.argv[1]
    texture = "--no-texture" not in sys.argv

    generate_3d_model(image_path=image_path, texture=texture)
