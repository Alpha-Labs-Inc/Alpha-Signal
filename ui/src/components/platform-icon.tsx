import React from 'react';

interface PlatformIconProps {
    platform: string;
    className?: string;
}

const PlatformIcon: React.FC<PlatformIconProps> = ({ platform, className = '' }) => {
    const renderIcon = () => {
        switch (platform?.toLowerCase()) {
            case 'twitter':
            case 'x':
                return (
                    <img
                        src="/X_logo_2023.svg"
                        alt="X/Twitter"
                        className={`w-4 h-4 filter invert brightness-0 ${className}`}
                    />
                );
            default:
                return null;
        }
    };

    return renderIcon();
};

export default PlatformIcon;