import { UserResponse } from '@/types';

interface UserAvatarProps {
  user: UserResponse | null;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const UserAvatar: React.FC<UserAvatarProps> = ({ user, size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-16 h-16 text-lg',
  };

  const getInitials = (name: string): string => {
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  if (!user) {
    return (
      <div
        className={`${sizeClasses[size]} ${className} rounded-full bg-gray-300 flex items-center justify-center`}
      >
        <span className="text-gray-600 font-medium">?</span>
      </div>
    );
  }

  if (user.avatar_url) {
    return (
      <img
        src={user.avatar_url}
        alt={user.full_name}
        className={`${sizeClasses[size]} ${className} rounded-full object-cover`}
      />
    );
  }

  // Fallback to initials
  const initials = getInitials(user.full_name);
  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-yellow-500',
    'bg-red-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
  ];

  // Use email to consistently pick a color
  const colorIndex = user.email.charCodeAt(0) % colors.length;
  const bgColor = colors[colorIndex];

  return (
    <div
      className={`${sizeClasses[size]} ${bgColor} ${className} rounded-full flex items-center justify-center text-white font-medium`}
    >
      {initials}
    </div>
  );
};
