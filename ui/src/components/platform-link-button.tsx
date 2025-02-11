import React from 'react';
import { ExternalLink } from 'lucide-react';

interface PlatformLinkButtonProps {
    platform: string;
    signal: string;
}

const PlatformLinkButton: React.FC<PlatformLinkButtonProps> = ({ platform, signal }) => {
    return (
        <a
            href={`https://x.com/${signal}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 px-2 py-1 text-sm text-white hover:text-black transition-colors rounded-md hover:bg-gray-100"
            title={`Visit ${signal} on ${platform}`}
        >
            <ExternalLink size={16} />
        </a>
    );
};

export default PlatformLinkButton;