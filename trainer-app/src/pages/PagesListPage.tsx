import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Edit, Eye, Trash, Globe } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useSubscription } from '@/hooks/useSubscription';
import { LimitReachedPrompt } from '@/components/LimitReachedPrompt';
import { apiClient } from '@/api/client';
import type { Page } from '@/types';

export default function PagesListPage() {
  const [pages, setPages] = useState<Page[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { hasReachedLimit, getLimit } = useSubscription();

  useEffect(() => {
    fetchPages();
  }, []);

  const fetchPages = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.get<Page[]>('/pages/');
      setPages(data as any);
    } catch (err) {
      console.error('Failed to load pages:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (pageId: number) => {
    if (!confirm('Are you sure you want to delete this page?')) {
      return;
    }

    try {
      await apiClient.delete(`/pages/${pageId}/`);
      await fetchPages();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete page');
    }
  };

  const limit = getLimit('pages');
  const isLimitReached = hasReachedLimit('pages', pages.length);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Pages</h1>
          <p className="text-muted-foreground mt-1">
            {pages.length} page{pages.length !== 1 ? 's' : ''}
            {limit !== -1 && ` / ${limit} limit`}
          </p>
        </div>
        <Link to="/pages/new">
          <Button disabled={isLimitReached}>
            <Plus className="mr-2 h-4 w-4" />
            Create Page
          </Button>
        </Link>
      </div>

      {isLimitReached && (
        <div className="mb-6">
          <LimitReachedPrompt
            resource="pages"
            currentCount={pages.length}
            limit={limit}
          />
        </div>
      )}

      {isLoading ? (
        <Card>
          <CardContent className="py-12">
            <p className="text-center text-muted-foreground">Loading pages...</p>
          </CardContent>
        </Card>
      ) : pages.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <p className="text-center text-muted-foreground mb-4">No pages yet</p>
            <div className="text-center">
              <Link to="/pages/new">
                <Button disabled={isLimitReached}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Your First Page
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {pages.map((page) => (
            <Card key={page.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle>{page.title}</CardTitle>
                    <CardDescription className="mt-1">
                      Slug: {page.slug}
                    </CardDescription>
                  </div>
                  {page.is_published && (
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded flex items-center gap-1">
                      <Globe className="h-3 w-3" />
                      Published
                    </span>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <Link to={`/pages/${page.id}/edit`} className="flex-1">
                    <Button variant="outline" className="w-full" size="sm">
                      <Edit className="mr-2 h-3 w-3" />
                      Edit
                    </Button>
                  </Link>
                  {page.public_url && (
                    <a href={page.public_url} target="_blank" rel="noopener noreferrer">
                      <Button variant="outline" size="sm">
                        <Eye className="h-3 w-3" />
                      </Button>
                    </a>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(page.id)}
                  >
                    <Trash className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

