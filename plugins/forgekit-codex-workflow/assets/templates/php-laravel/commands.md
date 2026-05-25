# PHP Laravel 命令示例

```powershell
php -v
composer install
php artisan test
php artisan route:list
php artisan migrate --pretend
npm install
npm run build
```

## Local validation / 局部验证优先级

```powershell
php artisan test
php artisan route:list
php artisan migrate --pretend
npm run build
```

注意：

- `composer install`、`npm install` 会下载依赖，先确认。
- `php artisan migrate`、seed、queue worker、scheduler 会影响外部状态，必须先确认。
- `.env`、APP_KEY、数据库密码、第三方 token 不进 Git。
- 部署、队列重启、缓存清理和 storage link 属于发布动作，执行前确认。
