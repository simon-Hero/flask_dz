from config import Config


# 验证上传图片是否符合config中的ALLOW_FEXTENSIONS
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in Config.ALLOWED_EXTENSIONS

