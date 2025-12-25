'use client';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <p className="text-center text-sm text-gray-600">
          &copy; {currentYear} All rights reserved by Tayyab Fayyaz
        </p>
      </div>
    </footer>
  );
}
