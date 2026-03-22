#!/bin/bash
# 有爱插件 Mac 更新器 - 辅助脚本
# 用途：权限提升、文件替换、备份恢复

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 备份插件
backup_plugin() {
    local src="$1"
    local backup_dir="$2"
    
    if [ ! -d "$src" ]; then
        log_error "源目录不存在：$src"
        return 1
    fi
    
    mkdir -p "$backup_dir"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$backup_dir/backup_$timestamp"
    
    log_info "正在备份：$src -> $backup_path"
    cp -R "$src" "$backup_path"
    
    if [ $? -eq 0 ]; then
        log_info "✅ 备份成功：$backup_path"
        return 0
    else
        log_error "❌ 备份失败"
        return 1
    fi
}

# 替换插件文件
replace_plugin() {
    local new_files="$1"
    local target_dir="$2"
    
    if [ ! -d "$new_files" ]; then
        log_error "新文件目录不存在：$new_files"
        return 1
    fi
    
    log_info "正在复制文件到：$target_dir"
    
    # 需要管理员权限
    sudo cp -R "$new_files"/* "$target_dir/"
    
    if [ $? -eq 0 ]; then
        log_info "✅ 更新成功"
        return 0
    else
        log_error "❌ 更新失败，尝试恢复备份"
        return 1
    fi
}

# 恢复备份
restore_backup() {
    local backup_path="$1"
    local target_dir="$2"
    
    if [ ! -d "$backup_path" ]; then
        log_error "备份不存在：$backup_path"
        return 1
    fi
    
    log_warn "正在恢复备份..."
    sudo rm -rf "$target_dir"
    sudo cp -R "$backup_path" "$target_dir"
    
    if [ $? -eq 0 ]; then
        log_info "✅ 恢复成功"
        return 0
    else
        log_error "❌ 恢复失败"
        return 1
    fi
}

# 清理旧备份（保留最近 N 个）
cleanup_backups() {
    local backup_dir="$1"
    local keep_count="${2:-3}"
    
    if [ ! -d "$backup_dir" ]; then
        return 0
    fi
    
    log_info "清理旧备份（保留最近 $keep_count 个）..."
    
    # 列出所有备份，按时间排序，删除旧的
    local count=0
    for backup in $(ls -t "$backup_dir"/backup_* 2>/dev/null); do
        count=$((count + 1))
        if [ $count -gt $keep_count ]; then
            log_info "删除旧备份：$backup"
            rm -rf "$backup"
        fi
    done
}

# 检查权限
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        log_warn "当前没有管理员权限，部分操作可能失败"
        return 1
    else
        log_info "已获取管理员权限"
        return 0
    fi
}

# 显示帮助
show_help() {
    cat << EOF
有爱插件 Mac 更新器 - 辅助脚本

用法:
  $0 <命令> [参数]

命令:
  backup <源目录> <备份目录>     备份插件
  replace <新文件> <目标目录>    替换插件
  restore <备份> <目标目录>      恢复备份
  cleanup <备份目录> [数量]      清理旧备份
  check                          检查权限

示例:
  $0 backup /path/to/Interface /path/to/backups
  $0 replace /tmp/new/Interface /path/to/Warcraft
  $0 restore /path/to/backups/backup_20260322 /path/to/Warcraft/Interface

EOF
}

# 主程序
main() {
    case "$1" in
        backup)
            backup_plugin "$2" "$3"
            ;;
        replace)
            replace_plugin "$2" "$3"
            ;;
        restore)
            restore_backup "$2" "$3"
            ;;
        cleanup)
            cleanup_backups "$2" "${3:-3}"
            ;;
        check)
            check_permissions
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

main "$@"
